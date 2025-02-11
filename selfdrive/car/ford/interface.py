#!/usr/bin/env python3
# from panda import Panda
from selfdrive.car import STD_CARGO_KG, get_safety_config
from selfdrive.car.ford.values import CANFD_CARS, CAR, CarParams, Ecu, GearShifter, TransmissionType
from selfdrive.car.interfaces import CarInterfaceBase


class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long):
    ret.carName = "ford"
    if candidate in CANFD_CARS:
      pass
      # ret.safetyConfigs = [get_safety_config(CarParams.SafetyModel.noOutput),
      #                      get_safety_config(CarParams.SafetyModel.ford, Panda.FLAG_FORD_CANFD)]
    else:
      ret.safetyConfigs = [get_safety_config(CarParams.SafetyModel.ford)]

    # These cars have been put into dashcam only due to both a lack of users and test coverage.
    # These cars likely still work fine. Once a user confirms each car works and a test route is
    # added to selfdrive/car/tests/routes.py, we can remove it from this list.
    ret.dashcamOnly = candidate in {CAR.EDGE_MK2_5, CAR.EXPEDITION_MK4_5, CAR.F_150_LIGHTNING_MK1, CAR.F_150_MK14, CAR.MUSTANG_MACH_E_MK1}

    # curvature steering
    ret.steerControlType = CarParams.SteerControlType.curvature
    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 0.4
    ret.lateralTuning.pid.kpBP, ret.lateralTuning.pid.kiBP = [[0.], [0.]]
    ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.008], [0.]]
    ret.lateralTuning.pid.kf = 1.

    if candidate == CAR.BRONCO_SPORT_MK1:
      ret.wheelbase = 2.67
      ret.steerRatio = 17.7
      ret.mass = 1625 + STD_CARGO_KG

    elif candidate == CAR.EDGE_MK2_5:
      ret.wheelbase = 2.85
      ret.steerRatio = 15.0  # guess
      ret.mass = 1900 + STD_CARGO_KG

    elif candidate == CAR.ESCAPE_MK4:
      ret.wheelbase = 2.71
      ret.steerRatio = 17.7
      ret.mass = 1750 + STD_CARGO_KG

    elif candidate == CAR.EXPEDITION_MK4_5:
      ret.wheelbase = 3.11
      ret.steerRatio = 16.8  # Copied from Explorer
      ret.mass = 2500 + STD_CARGO_KG

    elif candidate == CAR.EXPLORER_MK6:
      ret.wheelbase = 3.025
      ret.steerRatio = 16.8
      ret.mass = 2050 + STD_CARGO_KG

    elif candidate == CAR.FOCUS_MK4:
      ret.wheelbase = 2.7
      ret.steerRatio = 13.8
      ret.mass = 1350 + STD_CARGO_KG

    elif candidate == CAR.F_150_LIGHTNING_MK1:
      ret.wheelbase = 3.696
      ret.steerRatio = 18.0  # guess
      ret.mass = 2750 + STD_CARGO_KG

    elif candidate == CAR.F_150_MK14:
      # depends on body style
      ret.wheelbase = 3.5
      ret.steerRatio = 18.0  # guess
      ret.mass = 2100 + STD_CARGO_KG

    elif candidate == CAR.MAVERICK_MK1:
      ret.wheelbase = 3.076
      ret.steerRatio = 16.2
      ret.mass = 1650 + STD_CARGO_KG

    elif candidate == CAR.MUSTANG_MACH_E_MK1:
      ret.wheelbase = 2.985
      ret.steerRatio = 17.0  # guess
      ret.mass = 2100 + STD_CARGO_KG

    else:
      raise ValueError(f"Unsupported car: {candidate}")

    # Auto Transmission: 0x732 ECU or Gear_Shift_by_Wire_FD1
    found_ecus = [fw.ecu for fw in car_fw]
    if Ecu.shiftByWire in found_ecus or 0x5A in fingerprint[0]:
      ret.transmissionType = TransmissionType.automatic
    else:
      ret.transmissionType = TransmissionType.manual
      # TODO: add footnote
      #ret.minEnableSpeed = 20.0 * CV.MPH_TO_MS

    # BSM: Side_Detect_L_Stat, Side_Detect_R_Stat
    # TODO: detect bsm in car_fw?
    ret.enableBsm = 0x3A6 in fingerprint[0] and 0x3A7 in fingerprint[0]

    # LCA can steer down to zero
    ret.minSteerSpeed = 0.

    ret.autoResumeSng = ret.minEnableSpeed == -1.
    ret.centerToFront = ret.wheelbase * 0.44
    return ret

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)

    events = self.create_common_events(ret, extra_gears=[GearShifter.manumatic])
    ret.events = events.to_msg()

    return ret

  def apply(self, c):
    return self.CC.update(c, self.CS)
