# -- coding: utf-8 --

import sys
import platform
import threading
import os
from ctypes import *
from time import time
import cv2
import numpy as np

from .camera import CameraOperation

# 兼容不同操作系统加载 动态库
currentsystem = platform.system()
if currentsystem == 'Windows':
    _mvcam_env = os.getenv('MVCAM_COMMON_RUNENV')
    if _mvcam_env:
        sys.path.append(os.path.join(_mvcam_env, "Samples", "Python", "MvImport"))
else:
    sys.path.append(os.path.join("..", "..", "MvImport"))

from MvCameraControl_class import *


class CameraGrabber():
    def __init__(self, camera_name=""):
        MvCamera.MV_CC_Initialize()
        CameraOperation.set_exposure_time = 60000

        SDKVersion = MvCamera.MV_CC_GetSDKVersion()
        print ("SDKVersion[0x%x]" % SDKVersion)
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                      | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
        
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            print ("enum devices fail! ret[0x%x]" % ret)
            sys.exit()

        if deviceList.nDeviceNum == 0:
            print ("find no device!")
            sys.exit()

        print ("Find %d devices!" % deviceList.nDeviceNum)

        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
                print ("\ngige device: [%d]" % i)
                strModeName = self.decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print ("device model name: %s" % strModeName)
                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print ("\nu3v device: [%d]" % i)
                strModeName = self.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print ("device model name: %s" % strModeName)
                strSerialNumber = self.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber)                
                print ("user serial number: %s" % strSerialNumber)
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
                print ("\nCML device: [%d]" % i)
                strModeName = self.decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chModelName)
                print ("device model name: %s" % strModeName)
                strSerialNumber = self.decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chSerialNumber)
                print ("user serial number: %s" % strSerialNumber)
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CXP_DEVICE:
                print ("\nCXP device: [%d]" % i)
                strModeName = self.decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chModelName)
                print ("device model name: %s" % strModeName)
                strSerialNumber = self.decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chSerialNumber)
                print ("user serial number: %s" % strSerialNumber)
            elif mvcc_dev_info.nTLayerType == MV_GENTL_XOF_DEVICE:
                print ("\nXoF device: [%d]" % i)
                strModeName = self.decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chModelName)
                print ("device model name: %s" % strModeName)
                strSerialNumber = self.decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chSerialNumber)
                print ("user serial number: %s" % strSerialNumber)

        # 按摄像头名字查找设备
        nConnectionNum = -1
        if camera_name:
            for i in range(0, deviceList.nDeviceNum):
                mvcc_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
                user_name = ""
                if mvcc_info.nTLayerType == MV_USB_DEVICE:
                    user_name = self.decoding_char(mvcc_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                elif mvcc_info.nTLayerType == MV_GIGE_DEVICE or mvcc_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
                    user_name = self.decoding_char(mvcc_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                if user_name == camera_name:
                    nConnectionNum = i
                    print(f"[Camera] Found camera '{camera_name}' at index {i}")
                    break
            if nConnectionNum == -1:
                print(f"[Camera] Camera '{camera_name}' not found!")
                sys.exit()
        else:
            nConnectionNum = 0

        if int(nConnectionNum) >= deviceList.nDeviceNum:
            print ("intput error!")
            sys.exit()

        self.cam = MvCamera()
        stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

        ret = self.cam.MV_CC_CreateHandle(stDeviceList)
        if ret != 0:
            raise Exception ("create handle fail! ret[0x%x]" % ret)

        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if ret != 0:
            raise Exception ("open device fail! ret[0x%x]" % ret)
        
        if stDeviceList.nTLayerType == MV_GIGE_DEVICE or stDeviceList.nTLayerType == MV_GENTL_GIGE_DEVICE:
            nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                if ret != 0:
                    print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
            else:
                print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

        ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        if ret != 0:
            raise Exception ("set trigger mode fail! ret[0x%x]" % ret)

        # Set exposure after device is opened — settings don't take effect
        # on a device that hasn't been opened yet (e.g. after power cycle).
        ret = self.cam.MV_CC_SetEnumValue("ExposureAuto", 0)
        if ret != 0:
            print("Warning: set ExposureAuto fail! ret[0x%x]" % ret)
        ret = self.cam.MV_CC_SetFloatValue("ExposureTime", float(50000))
        if ret != 0:
            print("Warning: set ExposureTime fail! ret[0x%x]" % ret)
        else:
            print("ExposureTime set to 50000 us")

    def decoding_char(self, ctypes_char_array):
        byte_str = memoryview(ctypes_char_array).tobytes()
        null_index = byte_str.find(b'\x00')
        if null_index != -1:
            byte_str = byte_str[:null_index]
        for encoding in ['gbk', 'utf-8', 'latin-1']:
            try:
                return byte_str.decode(encoding)
            except UnicodeDecodeError:
                continue
        return byte_str.decode('latin-1', errors='replace')

    def grab_image(self):
        stOutFrame = MV_FRAME_OUT()  
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))
        ret = self.cam.MV_CC_GetImageBuffer(stOutFrame, 1000)
        if None != stOutFrame.pBufAddr and 0 == ret:
            print ("get one frame: Width[%d], Height[%d], nFrameNum[%d]"  % (stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameNum))
            nRGBSize = stOutFrame.stFrameInfo.nWidth * stOutFrame.stFrameInfo.nHeight * 3
            stConvertParam = MV_CC_PIXEL_CONVERT_PARAM_EX()
            memset(byref(stConvertParam), 0, sizeof(stConvertParam))
            stConvertParam.nWidth = stOutFrame.stFrameInfo.nWidth
            stConvertParam.nHeight = stOutFrame.stFrameInfo.nHeight
            stConvertParam.pSrcData = stOutFrame.pBufAddr
            stConvertParam.nSrcDataLen = stOutFrame.stFrameInfo.nFrameLen
            stConvertParam.enSrcPixelType = stOutFrame.stFrameInfo.enPixelType  
            stConvertParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed
            stConvertParam.pDstBuffer = (c_ubyte * nRGBSize)()
            stConvertParam.nDstBufferSize = nRGBSize

            ret = self.cam.MV_CC_ConvertPixelTypeEx(stConvertParam)
            if ret != 0:
                raise Exception ("convert pixel fail! ret[0x%x]" % ret)
            raw_data = (c_ubyte * nRGBSize).from_address(cast(stConvertParam.pDstBuffer, c_void_p).value)
            img_np = np.frombuffer(raw_data, dtype=np.uint8)
            img_color = img_np.reshape((stConvertParam.nHeight, stConvertParam.nWidth, 3)).copy()
            nRet = self.cam.MV_CC_FreeImageBuffer(stOutFrame)
            return img_color
        else:
            print ("no data[0x%x]" % ret)

    def start_grabbing(self):
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            raise Exception ("start grabbing fail! ret[0x%x]" % ret)
    
    def deal_image(self, mode, path_file, img_color):
        if mode == "save":
            cv2.imwrite(path_file, img_color)
        elif mode == "show":
             cv2.imshow("Industrial Camera", img_color)
             cv2.waitKey(0)

    def stop_grabbing(self):
        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            raise Exception ("stop grabbing fail! ret[0x%x]" % ret)

    def close(self):
        ret = self.cam.MV_CC_CloseDevice()
        if ret != 0:
            raise Exception ("close deivce fail! ret[0x%x]" % ret)
        self.cam.MV_CC_DestroyHandle()
