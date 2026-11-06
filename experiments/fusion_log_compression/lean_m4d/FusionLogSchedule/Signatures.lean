import FusionLogSchedule

set_option pp.universes true in
#check @FusionLogSchedule.abstract_schedule_endpoint_iff

set_option pp.universes true in
#check @FusionLogSchedule.abstract_schedule_bounded_realization

set_option pp.universes true in
#check @FusionLogSchedule.abstract_schedule_endpoint_iff_bounded

#print FusionLogSchedule.AdmissibleSchedule
#print FusionLogSchedule.CompatibleForLog
#print FusionLogSchedule.PacketPartition
