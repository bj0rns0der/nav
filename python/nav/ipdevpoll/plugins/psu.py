# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
""" ipdevpolld plugin to collect redundant power-supply units and status
for the power-supplies.

This plugin uses ENTITY-MIB to retrieve all possible PSUs in network-
equipment.

Status for fans  in Cisco-equipment is collected with
CISCO-ENTITY-FRU-CONTROL-MIB.
"""

from twisted.internet import defer

from nav.ipdevpoll import Plugin
from nav.ipdevpoll import shadows

from nav.mibs.entity_mib import EntityMib
from nav.mibs.entity_mib import EntityTable
from nav.mibs.entity_sensor_mib import EntitySensorMib
from nav.mibs.cisco_entity_fru_control_mib import CiscoEntityFruControlMib
from nav.mibs.hp_icf_chassis import HpIcfChassis

VENDOR_CISCO = 9
VENDOR_HP = 11

class PowerSupplyUnit(Plugin):
    """Plugin that collect PSUs from netboxes."""
    vendor_id = None

    def __init__(self, *args, **kwargs):
        super(PowerSupplyUnit, self).__init__(*args, **kwargs)
        self.entity_mib = EntityMib(self.agent)
        self.entity_sensor_mib = EntitySensorMib(self.agent)
        self.entity_fru_control = None
        if self.netbox.type:
            self.vendor_id = self.netbox.type.get_enterprise_id()
        if self.vendor_id == VENDOR_CISCO:
            self.entity_fru_control = CiscoEntityFruControlMib(self.agent)
        elif self.vendor_id == VENDOR_HP:
            self.entity_fru_control = HpIcfChassis(self.agent)

    @classmethod
    def can_handle(cls, netbox):
        return True
    def _get_redundant_psus_and_fans(self, to_filter):
        """ Filter out PSUs and FANs, and return only redundant."""
        filtered = []
        for key, values in to_filter.items():
            if to_filter[key]['entPhysicalClass'] in ['powerSupply', 'fan']:
                filtered.append(values)
        # weed out boxes with only one PSU
        if len(filtered) < 2:
            filtered = []
        return filtered

    def is_fan(self, pwr):
        return (pwr.get('entPhysicalClass', None) == 'fan')

    def is_psu(self, pwr):
        return (pwr.get('entPhysicalClass', None) == 'powerSupply')

    @defer.inlineCallbacks
    def handle(self):
        self._logger.error("Collecting PSUs")
        entity_table = yield self.entity_mib.get_entity_physical_table()
        psus_and_fans = self._get_redundant_psus_and_fans(entity_table)
        if psus_and_fans:
            for psu_or_fan in psus_and_fans:
                self._logger.error('PSU:FAN: %s' % psu_or_fan)
                entity_index = psu_or_fan.get(0, None)
                up = 'n'
                sensor_oid = None
                if self.entity_fru_control:
                    if self.is_fan(psu_or_fan):
                        # locate sensor and get status
                        ret = yield self.entity_fru_control.is_fan_up(
                                                                entity_index)
                        if ret:
                            up = 'y'
                            sensor_oid = (
                                self.entity_fru_control.get_oid_for_fan_status(
                                                                entity_index))
                        self._logger.error('FAN: %s: %s' % (ret, sensor_oid))
                    elif self.is_psu(psu_or_fan):
                        ret = yield self.entity_fru_control.is_psu_up(
                                                                entity_index)
                        if ret:
                            up = 'y'
                            sensor_oid = (
                                self.entity_fru_control.get_oid_for_psu_status(
                                                                entity_index))
                        self._logger.error('PSU: %s: %s' % (ret, sensor_oid))
                power_supply = self.containers.factory(entity_index,
                                                        shadows.PowerSupply)
                # psu info
                power_supply.netbox = self.netbox
                power_supply.name = psu_or_fan.get('entPhysicalName', None)
                power_supply.model = psu_or_fan.get('entPhysicalModelName',
                                                                        None)
                power_supply.descr = psu_or_fan.get('entPhysicalDescr', None)
                power_supply.physical_class = psu_or_fan.get(
                                                    'entPhysicalClass', None)
                power_supply.sensor_oid = sensor_oid
                power_supply.up = up
                # device info
                serial = psu_or_fan.get('entPhysicalSerialNum', None)
                if serial:
                    device = self.containers.factory(entity_index,
                                                        shadows.Device)
                    device.serial = serial
                    device.hardware_version = psu_or_fan.get(
                                                'entPhysicalHardwareRev', None)
                    device.firmware_version = psu_or_fan.get(
                                                'entPhysicalFirmwareRev', None)
                    device.software_version = psu_or_fan.get(
                                                'entPhysicalSoftwareRev', None)
                    power_supply.device = device
