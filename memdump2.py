import can
import time

padding = [0x00 for _ in range(0x40)]
bus = can.interface.Bus(interface='socketcan', channel='vcan0', bitrate=500000)
more_message = can.Message(arbitration_id=0x7E0, dlc=0x3, data=[0x30, 0x00, 0x00], is_extended_id=False)

# "merged_dump.bin" 파일을 미리 열어서 계속 데이터를 추가함
with open("merged_dump.bin", "wb") as outfile:
    for addr in range(0x400000, 0x500000, 0x10000):
        for hex_value in range(addr, addr + 0x10000, 0x40):
            byte1 = (hex_value >> 24) & 0xff
            byte2 = (hex_value >> 16) & 0xff
            byte3 = (hex_value >> 8) & 0xff
            byte4 = hex_value & 0xff

            msg1 = can.Message(
                arbitration_id=0x7E0,
                dlc=0x8,
                data=[0x07, 0x23, 0x14, byte1, byte2, byte3, byte4, 0x40],
                is_extended_id=False
            )
            bus.send(msg1)
            time.sleep(0.01)
            recv_msg = list(bus.recv().data)
            if recv_msg[1] == 0x7F:
                print(f"skipping address at {hex(hex_value)}")
                recv_msg += padding
                continue

            # 첫 프레임의 데이터 (인덱스 2~6, 5바이트)를 바로 파일에 기록
            outfile.write(bytes(recv_msg[2:7]))

            size = 0x3A
            bus.send(more_message)
            while size > 0:
                # 추가 데이터 프레임 수신 (먼저 1~6번째 바이트 슬라이싱 후, 다시 1~6번째 바이트를 기록)
                recv_msg = list(bus.recv().data[1:7])
                size -= 0x7
                outfile.write(bytes(recv_msg[1:7]))
        outfile.flush()
