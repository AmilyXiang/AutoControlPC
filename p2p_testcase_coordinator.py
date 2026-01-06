"""
p2p_testcase_coordinator.py
P2P网络协调器 - 使用对等网络同步执行testcase
"""
import sys
import threading
from remote_controller import RemoteController


class P2PTestcaseCoordinator:
    """使用P2P网络协调两个testcase的执行"""
    
    def __init__(self, pc1_host, pc1_port, pc2_host, pc2_port):
        """
        初始化协调器
        
        Args:
            pc1_host: PC-1 IP
            pc1_port: PC-1 服务器端口
            pc2_host: PC-2 IP
            pc2_port: PC-2 服务器端口
        """
        self.pc1 = RemoteController(pc1_host, pc1_port)
        self.pc2 = RemoteController(pc2_host, pc2_port)
        self.results = {'pc1': None, 'pc2': None}

    def connect_all(self):
        """连接到两个PC的remote_executor服务器"""
        print("[P2P-COORD] 连接PC-1...")
        if not self.pc1.connect():
            return False
        
        print("[P2P-COORD] 连接PC-2...")
        if not self.pc2.connect():
            self.pc1.disconnect()
            return False
        
        print("[P2P-COORD] 已连接到两个PC")
        return True

    def disconnect_all(self):
        """断开连接"""
        self.pc1.disconnect()
        self.pc2.disconnect()

    def run_simultaneous(self, pc1_xml, pc1_testcase, pc2_xml, pc2_testcase):
        """
        同时运行两个PC上的testcase
        
        PC之间通过P2P网络通信，无需第三方协调
        
        Args:
            pc1_xml: PC-1 testcase文件
            pc1_testcase: PC-1 testcase名称
            pc2_xml: PC-2 testcase文件
            pc2_testcase: PC-2 testcase名称
        """
        print(f"\n[P2P-COORD] 开始P2P协调执行")
        print(f"[P2P-COORD] PC-1: {pc1_xml} / {pc1_testcase}")
        print(f"[P2P-COORD] PC-2: {pc2_xml} / {pc2_testcase}\n")
        
        def run_pc1():
            print("[P2P-COORD] [PC-1] 开始执行...")
            response = self.pc1.run_testcase(pc1_xml, pc1_testcase)
            self.results['pc1'] = response
            print(f"[P2P-COORD] [PC-1] 执行完成: {response}")

        def run_pc2():
            print("[P2P-COORD] [PC-2] 开始执行...")
            response = self.pc2.run_testcase(pc2_xml, pc2_testcase)
            self.results['pc2'] = response
            print(f"[P2P-COORD] [PC-2] 执行完成: {response}")

        # 同时启动两个线程
        thread1 = threading.Thread(target=run_pc1, daemon=True)
        thread2 = threading.Thread(target=run_pc2, daemon=True)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        print(f"\n[P2P-COORD] 执行完成")
        print(f"[P2P-COORD] PC-1结果: {self.results['pc1']}")
        print(f"[P2P-COORD] PC-2结果: {self.results['pc2']}")
        
        return self.results


def main():
    if len(sys.argv) < 9:
        print("用法: python p2p_testcase_coordinator.py <pc1_host> <pc1_port> <pc2_host> <pc2_port> <pc1_xml> <pc1_testcase> <pc2_xml> <pc2_testcase>")
        print("\n示例 (Call端和Answer端并发执行):")
        print("  python p2p_testcase_coordinator.py 127.0.0.1 9999 192.168.1.101 9999 \\")
        print("    testcase/p2p_network_demo.xml \"Call端流程\" \\")
        print("    testcase/p2p_network_demo.xml \"Answer端流程\"")
        sys.exit(1)
    
    pc1_host = sys.argv[1]
    pc1_port = int(sys.argv[2])
    pc2_host = sys.argv[3]
    pc2_port = int(sys.argv[4])
    pc1_xml = sys.argv[5]
    pc1_testcase = sys.argv[6]
    pc2_xml = sys.argv[7]
    pc2_testcase = sys.argv[8]
    
    coordinator = P2PTestcaseCoordinator(pc1_host, pc1_port, pc2_host, pc2_port)
    
    if not coordinator.connect_all():
        print("[P2P-COORD] 连接失败")
        sys.exit(1)
    
    try:
        coordinator.run_simultaneous(pc1_xml, pc1_testcase, pc2_xml, pc2_testcase)
    finally:
        coordinator.disconnect_all()


if __name__ == '__main__':
    main()
