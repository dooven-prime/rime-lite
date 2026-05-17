from collections.abc import Mapping
from functools import wraps
import os, io, sys, pickle

import time
from contextlib import contextmanager

# 项目根目录下的 data/，无论从哪里运行都指向同一位置
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_PROJECT_ROOT, 'data')
DATA_CACHE_DIR = os.path.join(DATA_DIR, 'cache')
DATA_PROPS_DIR = os.path.join(DATA_DIR, 'props')

try:
    import joblib
    _HAS_JOBLIB = True
except ImportError:
    joblib = None
    _HAS_JOBLIB = False
    
@contextmanager
def timer(name):
    t0 = time.perf_counter()
    yield
    t1 = time.perf_counter()
    print(f"[TIME] {name}: {t1 - t0:.4f}s")

def setup_utf8_stdout():
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass  # stdout already configured or not wrappable

def _save_obj(obj, filepath: str) -> None:
    """Save object to file — joblib if available, else pickle."""
    if _HAS_JOBLIB:
        joblib.dump(obj, filepath)
    else:
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)


def _load_obj(filepath: str):
    """Load object from file — joblib if available, else pickle."""
    if _HAS_JOBLIB:
        return joblib.load(filepath)
    with open(filepath, 'rb') as f:
        return pickle.load(f)
    
class IndexProxy(Mapping):
    """
    兼容：
      proxy[key]
      proxy.get(key)
      proxy()
    """

    def __init__(self, data: dict | list | tuple):
        self._data = data

    def __getitem__(self, key):
        if isinstance(self._data, dict) and key not in self._data:
            raise KeyError(f"Invalid key: {key}")
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    @property
    def raw(self):
        return self._data  # 直接访问,只读视图

    def __call__(self):
        return self

    def __contains__(self, key) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"

    def items(self):
        return self._data.items()  # dict 方法透传

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def update(self, **kwargs):
        if isinstance(self._data, dict):
            self._data.update(**kwargs)
        else:
            raise AttributeError("update() only for dict")

    def index(self, value, start=0, end=None):
        if isinstance(self._data, (list, tuple)):
            return self._data.index(value, start, end)
        raise AttributeError("index() only supported for list/tuple")

    def clear(self):
        self._data.clear()

    def copy(self):
        """返回原数据的浅拷贝"""
        return self._data.copy() if hasattr(self._data, 'copy') else type(self._data)(self._data)


class class_property:
    """
    带缓存的 class-level property
    第一次访问计算，之后缓存到类
    自定义缓存属性名，适合无参或固定参数的懒加载。
    用于懒加载（lazy load）型类属性。仅检查当前类。
    """

    def __init__(self, attr_name: str = None):
        self.attr_name = attr_name
        self.func = None

    def __call__(self, func):
        self.func = func
        self.attr_name = self.attr_name or func.__name__.upper()
        return self

    def __get__(self, obj, cls):
        if not hasattr(cls, self.attr_name):
            raw = self.func(cls)
            if isinstance(raw, (dict, list, tuple)):
                raw = IndexProxy(raw)
            setattr(cls, self.attr_name, raw)
        return getattr(cls, self.attr_name)

    def __set_name__(self, owner, name):
        if not hasattr(owner, '_class_prop_names'):
            owner._class_prop_names = []
        owner._class_prop_names.append(name)

        if not hasattr(owner, '_class_cache_names'):
            owner._class_cache_names = []
        owner._class_cache_names.append(self.attr_name)

    @staticmethod
    def class_property(attr_name: str):
        """
        缓存装饰器，支持首次调用生成值并缓存到类属性。
        """

        def decorator(func) -> classmethod:
            def wrapper(cls, *args):
                if not hasattr(cls, attr_name):
                    setattr(cls, attr_name, func(cls, *args))
                return getattr(cls, attr_name)

            return classmethod(wrapper)

        return decorator
    
    @staticmethod
    def trigger_properties(cls):
        """
        触发类中所有 class_property 的计算，确保它们被缓存。
        可在需要时调用，或在 save/load 前自动调用。
        """
        for prop_name in getattr(cls, '_class_prop_names', []):
            _ = getattr(cls, prop_name) # triggers __get__ → caches result

    @staticmethod
    def save(cls, prop_dir=None):
        """
        保存类的所有 class_property 缓存值到文件。
        自动触发计算并保存，无需指定属性名。
        """
        if prop_dir is None:
            prop_dir = DATA_PROPS_DIR
        os.makedirs(prop_dir, exist_ok=True)

        # 触发所有懒加载计算并缓存结果
        class_property.trigger_properties(cls) 

        for cache_name in getattr(cls, '_class_cache_names', []):
            if not isinstance(cache_name, str):
                print(f"Warning: skipping non-string cache name {cache_name!r} (type {type(cache_name).__name__})")
                continue
            if hasattr(cls, cache_name):
                value = getattr(cls, cache_name)
                _save_obj(value, f'{prop_dir}/{cls.__name__}_{cache_name}.pkl')
        print(f"Class {cls.__name__} properties saved to {prop_dir}")

    @staticmethod
    def load(cls, prop_dir=None):
        """
        加载保存的类属性值，并设置回类。
        自动处理所有已注册的缓存属性，无需指定属性名。
        """
        if prop_dir is None:
            prop_dir = DATA_PROPS_DIR
        for cache_name in getattr(cls, '_class_cache_names', []):
            prop_path = f'{prop_dir}/{cls.__name__}_{cache_name}.pkl'
            if os.path.exists(prop_path):
                value = _load_obj(prop_path)
                setattr(cls, cache_name, value)
        print(f"Class {cls.__name__} properties loaded from {prop_dir}")


# lru_cache
class class_cache:
    def __init__(self, cache_name: str = None, key=None):
        self.cache_name = cache_name
        self.key_func = key
        self.func = None

    def __call__(self, func):
        self.func = func
        if self.cache_name is None:
            self.cache_name = f"_{func.__name__}_cache".upper()
        return self

    def __get__(self, obj, cls):
        cache = cls.__dict__.get(self.cache_name)
        if cache is None:
            cache = {}
            setattr(cls, self.cache_name, cache)

        bound = self.func.__get__(obj, cls)  # self.func.__func__/self.func(cls,...

        def wrapper(*args, **kwargs):
            key = self.key_func(*args, **kwargs) if self.key_func else (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                cache[key] = bound(*args, **kwargs)
            return cache[key]

        wrapper.cache = cache
        return wrapper

    def __set_name__(self, owner, name):
        # if not isinstance(self.cache_name, str):
        #     self.cache_name = str(self.cache_name)  # 转为字符串
        if not hasattr(owner, '_class_cache_names'):
            owner._class_cache_names = []
        owner._class_cache_names.append(self.cache_name)

    @staticmethod
    def save(cls, cache_dir=None):
        """
        保存类的所有 class_cache 缓存字典到文件。
        自动保存现有缓存，无需指定名称。
        """
        if cache_dir is None:
            cache_dir = DATA_CACHE_DIR
        os.makedirs(cache_dir, exist_ok=True)

        for cache_name in getattr(cls, '_class_cache_names', []):
            if not isinstance(cache_name, str):
                print(f"Warning: skipping non-string cache name {cache_name!r} (type {type(cache_name).__name__})")
                continue
            if hasattr(cls, cache_name):
                cache = getattr(cls, cache_name)
                _save_obj(cache, f'{cache_dir}/{cls.__name__}_{cache_name}.pkl')
        print(f"Class {cls.__name__} cache saved to {cache_dir}")

    @staticmethod
    def load(cls, cache_dir=None):
        """
        加载保存的类缓存字典，并设置回类。
        自动处理所有已注册的缓存名称。
        """
        if cache_dir is None:
            cache_dir = DATA_CACHE_DIR
        for cache_name in getattr(cls, '_class_cache_names', []):
            cache_path = f'{cache_dir}/{cls.__name__}_{cache_name}.pkl'
            if os.path.exists(cache_path):
                cache = _load_obj(cache_path)
                setattr(cls, cache_name, cache)
        print(f"Class {cls.__name__} cache loaded from {cache_dir}")


def chainable_method(func):
    """装饰器，使方法支持链式调用，保留显式返回值"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return self if result is None else result

    return wrapper


def class_status(state: str = 'TODO', notes=None):
    """标记方法状态的装饰器，不改变原方法行为。
    '未实现''已废弃''待完成''实验性''有BUG''参考方法'
    """

    def decorator(func):
        func._method_status = {"state": state, "notes": notes}
        return func

    return decorator


def check_class_status(cls):
    """检查类中所有方法的状态，返回字典。"""
    status_dict = {}
    for name in dir(cls):
        if not name.startswith('_'):
            attr = getattr(cls, name)
            if callable(attr):
                status_info = getattr(attr, '_method_status', None)
                if status_info:
                    status_dict[name] = status_info
    return status_dict
