"""
p2p_network.py
P2P对等网络通信 - 两方都能发送和接收消息
"""
import socket
import json
import threading
import time
from network_event import NetworkEvent, EVENTS


class P2PNetwork:
    """P2P对等网络 - 同时支持接收和发送"""
    
    def __init__(self, local_port=9998, peer_host=None, peer_port=9998):
        """
        初始化P2P网络
        
        Args:
            local_port: 本地监听端口
            peer_host: 对端地址（可选，连接时提供）
            peer_port: 对端端口
        """
        self.local_port = local_port
        self.peer_host = peer_host
        self.peer_port = peer_port
        
        self.server_socket = None       # 接收方socket
        self.client_socket = None       # 发送方socket
        self.running = False
        self.receive_thread = None
        self.message_queue = []         # 接收到的消息队列
        self.message_lock = threading.Lock()
        
        # 获取本机IP地址
        self.local_ip = self._get_local_ip()

    def _get_local_ip(self):
        """获取本机可用的IP地址"""
        try:
            # 尝试连接到对端，从而获取本机对外的IP
            if self.peer_host:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((self.peer_host, self.peer_port or 9999))
                ip = s.getsockname()[0]
                s.close()
                return ip
        except:
            pass
        
        # 备选方案：获取第一个非环回地址
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _start_server(self):
        """启动接收服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.local_port))
            self.server_socket.listen(5)
            self.running = True
            
            # 在独立线程中接收消息
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            print(f"[P2P] ✓ 接收服务器启动")
            print(f"[P2P]   本地端口: {self.local_port}")
            print(f"[P2P]   可连接地址: {self.local_ip}:{self.local_port}")
        except Exception as e:
            print(f"[P2P] 启动接收服务器失败: {e}")
            return False

    def _receive_loop(self):
        """接收消息循环"""
        try:
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"[P2P] 收到连接: {addr}")
                    
                    # 在新线程处理连接
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr),
                        daemon=True
                    )
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"[P2P] 接收错误: {e}")
        except Exception as e:
            print(f"[P2P] 接收循环出错: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_client(self, client_socket, addr):
        """处理客户端连接"""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    
                    # 将消息加入队列
                    with self.message_lock:
                        self.message_queue.append(message)
                    
                    print(f"[P2P] 收到消息: {message}")
                except json.JSONDecodeError:
                    print(f"[P2P] 无效的JSON: {data}")
        except Exception as e:
            print(f"[P2P] 客户端处理错误: {e}")
        finally:
            client_socket.close()

    def _connect_to_peer(self):
        """连接到对端（带重试机制）"""
        if not self.peer_host:
            print(f"[P2P] 跳过连接: peer_host为空")
            return False
        
        max_retries = 5
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                print(f"[P2P] 尝试连接到对端 {self.peer_host}:{self.peer_port} (第 {attempt+1}/{max_retries} 次)...")
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.settimeout(10)  # 设置10秒连接超时
                self.client_socket.connect((self.peer_host, self.peer_port))
                self.client_socket.settimeout(None)  # 连接成功后移除超时
                print(f"[P2P] ✓ 已连接到对端 {self.peer_host}:{self.peer_port}")
                return True
            except socket.timeout:
                print(f"[P2P] 连接超时 (WinError 10060)，{retry_delay}秒后重试...")
                self.client_socket = None
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print(f"[P2P] ✗ 连接失败: 达到最大重试次数")
                    return False
            except Exception as e:
                print(f"[P2P] 连接失败: {e}")
                self.client_socket = None
                if attempt < max_retries - 1:
                    print(f"[P2P] {retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False

    def send(self, event, data=None, timeout=5):
        """
        发送消息
        
        Args:
            event: 事件名称或NetworkEvent枚举
            data: 事件数据
            timeout: 发送超时时间（秒）
        
        Returns:
            成功返回True，失败返回False
        """
        if isinstance(event, NetworkEvent):
            event_name = event.value
        else:
            event_name = str(event)
        
        message = {
            'event': event_name,
            'data': data or {},
            'timestamp': time.time()
        }
        
        try:
            # 如果还没有连接，尝试连接
            if not self.client_socket:
                print(f"[P2P] 发送前检查: client_socket为None，peer_host={self.peer_host}:{self.peer_port}")
                if not self._connect_to_peer():
                    print(f"[P2P] 发送失败: 无法连接到对端")
                    return False
            
            if self.client_socket:
                try:
                    self.client_socket.sendall(json.dumps(message).encode('utf-8'))
                    print(f"[P2P] 发送消息: {event_name}, 数据: {data}")
                    return True
                except Exception as e:
                    # 连接可能已断开，清除socket重试
                    print(f"[P2P] 发送出错，尝试重新连接: {e}")
                    self.client_socket = None
                    if self._connect_to_peer():
                        self.client_socket.sendall(json.dumps(message).encode('utf-8'))
                        print(f"[P2P] 重连后发送成功: {event_name}")
                        return True
                    return False
            else:
                print(f"[P2P] 发送失败: 未连接到对端")
                return False
        except Exception as e:
            print(f"[P2P] 发送错误: {e}")
            return False

    def receive(self, event=None, timeout=30):
        """
        接收消息（阻塞等待）
        
        Args:
            event: 等待的事件名称（None表示接收任何事件）
            timeout: 等待超时时间（秒）
        
        Returns:
            收到的消息字典，超时返回None
        """
        if isinstance(event, NetworkEvent):
            target_event = event.value
        else:
            target_event = str(event) if event else None
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.message_lock:
                # 查找匹配的消息
                for i, msg in enumerate(self.message_queue):
                    if target_event is None or msg.get('event') == target_event:
                        # 找到匹配的消息，移除并返回
                        self.message_queue.pop(i)
                        print(f"[P2P] 接收消息: {msg.get('event')}, 数据: {msg.get('data')}")
                        return msg
            
            time.sleep(0.1)  # 短暂等待后重试
        
        print(f"[P2P] 接收消息超时 (事件: {target_event}, 超时: {timeout}秒)")
        return None

    def stop(self):
        """停止网络连接"""
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        print("[P2P] 网络已停止")


# 全局网络实例
_global_network = None


def get_network():
    """获取全局网络实例"""
    global _global_network
    if _global_network is None:
        _global_network = P2PNetwork()
    return _global_network


def init_network(local_port=9998, peer_host=None, peer_port=9998):
    """初始化全局网络"""
    global _global_network
    _global_network = P2PNetwork(local_port, peer_host, peer_port)
    if peer_host:
        _global_network.init(peer_host, peer_port)
    else:
        _global_network._start_server()
    return _global_network


def stop_network():
    """停止全局网络"""
    global _global_network
    if _global_network:
        _global_network.stop()
        _global_network = None


if __name__ == '__main__':
    # 测试P2P网络
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python p2p_network.py <mode> [args...]")
        print("  模式1 (接收方): python p2p_network.py receiver 9998")
        print("  模式2 (发送方): python p2p_network.py sender 192.168.1.100 9998 9999")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'receiver':
        local_port = int(sys.argv[2]) if len(sys.argv) > 2 else 9998
        network = P2PNetwork(local_port=local_port)
        network._start_server()
        
        print(f"[TEST] 接收模式: 监听端口 {local_port}")
        print("[TEST] 等待消息...")
        
        try:
            while True:
                msg = network.receive(timeout=60)
                if msg:
                    print(f"[TEST] 收到: {msg}")
                else:
                    print("[TEST] 超时，没有收到消息")
        except KeyboardInterrupt:
            network.stop()
    
    elif mode == 'sender':
        peer_host = sys.argv[2]
        peer_port = int(sys.argv[3]) if len(sys.argv) > 3 else 9998
        local_port = int(sys.argv[4]) if len(sys.argv) > 4 else 9999
        
        network = P2PNetwork(local_port=local_port)
        network.init(peer_host, peer_port)
        
        print(f"[TEST] 发送模式: 发送给 {peer_host}:{peer_port}")
        
        time.sleep(1)
        network.send(NetworkEvent.READY, {'message': 'hello'})
        network.stop()
