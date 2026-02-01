import subprocess
import sys
import os
import time
import psutil
import signal
from threading import Thread

class ProcessMonitor:
    """プロセスの実行を監視"""

    def __init__(self, timeout=300, memory_limit_mb=8192):
        """
        Args:
            timeout: タイムアウト秒数（デフォルト5分）
            memory_limit_mb: メモリ上限MB（デフォルト8GB）
        """
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.process = None
        self.timed_out = False
        self.memory_exceeded = False
        self.peak_memory = 0

    def check_memory(self):
        """メモリ使用量を監視"""
        try:
            if self.process and self.process.poll() is None:
                proc = psutil.Process(self.process.pid)
                # プロセスツリー全体のメモリ使用量を取得
                memory_mb = proc.memory_info().rss / 1024 / 1024

                # 子プロセスのメモリも含める
                try:
                    for child in proc.children(recursive=True):
                        memory_mb += child.memory_info().rss / 1024 / 1024
                except:
                    pass

                self.peak_memory = max(self.peak_memory, memory_mb)

                if memory_mb > self.memory_limit_mb:
                    self.memory_exceeded = True
                    return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return True

    def run(self, script_path, script_name):
        """スクリプトを安全に実行"""
        print(f"\n{'='*60}")
        print(f"実行: {script_name}")
        print(f"  タイムアウト: {self.timeout}秒")
        print(f"  メモリ上限: {self.memory_limit_mb}MB")
        print('='*60)

        start_time = time.time()

        try:
            # プロセスを起動
            self.process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # メモリ監視スレッド
            memory_check_interval = 1.0  # 1秒ごとにチェック

            while True:
                # プロセスが終了したかチェック
                retcode = self.process.poll()
                if retcode is not None:
                    break

                # 経過時間チェック
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    self.timed_out = True
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                    break

                # メモリチェック
                if not self.check_memory():
                    print(f"\n⚠ メモリ上限超過: {self.peak_memory:.1f}MB > {self.memory_limit_mb}MB")
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                    break

                time.sleep(memory_check_interval)

            # 出力を取得
            stdout, stderr = self.process.communicate()

            elapsed = time.time() - start_time

            # 結果を表示
            if self.timed_out:
                print(f"\n❌ タイムアウト ({self.timeout}秒経過)")
                print(f"   経過時間: {elapsed:.2f}秒")
                print(f"   ピークメモリ: {self.peak_memory:.1f}MB")
                return False

            elif self.memory_exceeded:
                print(f"\n❌ メモリ上限超過")
                print(f"   ピークメモリ: {self.peak_memory:.1f}MB > {self.memory_limit_mb}MB")
                print(f"   経過時間: {elapsed:.2f}秒")
                return False

            elif retcode != 0:
                print(f"\n❌ 実行エラー (終了コード: {retcode})")
                if stderr:
                    print("エラー出力:")
                    print(stderr)
                return False

            else:
                print(stdout)
                if stderr:
                    print("警告:")
                    print(stderr)
                print(f"\n✓ 成功 (経過時間: {elapsed:.2f}秒, ピークメモリ: {self.peak_memory:.1f}MB)")
                return True

        except Exception as e:
            print(f"\n❌ 予期しないエラー: {e}")
            if self.process:
                try:
                    self.process.kill()
                except:
                    pass
            return False


def get_file_size_mb(filepath):
    """ファイルサイズをMBで取得"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    return 0


def estimate_requirements(csv_file):
    """CSVファイルサイズから必要なリソースを推定"""
    file_size = get_file_size_mb(csv_file)

    # 推定値（経験則）
    # For-loop: メモリ使用量小、時間大
    # Pandas: メモリ使用量大（ファイルサイズの3-5倍）、時間中
    # Spark: メモリ使用量中、時間小

    estimates = {
        "for": {
            "memory_mb": max(500, file_size * 0.5),
            "timeout": max(300, file_size * 2)
        },
        "pandas": {
            "memory_mb": max(1000, file_size * 5),
            "timeout": max(180, file_size * 1)
        },
        "spark": {
            "memory_mb": max(2000, file_size * 3),
            "timeout": max(120, file_size * 0.5)
        }
    }

    return file_size, estimates


def main():
    csv_file = "DummyTaxiData.csv"

    # CSVファイルの存在確認
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} が見つかりません")
        print("先にデータ生成を実行してください:")
        print("  python 01_generateDummyTaxiData.py")
        return

    # ファイルサイズと推定リソース
    file_size, estimates = estimate_requirements(csv_file)

    print("="*60)
    print("安全実行モード")
    print("="*60)
    print(f"データファイル: {csv_file} ({file_size:.1f} MB)")
    print()
    print("推定リソース要件:")
    for name, est in estimates.items():
        print(f"  {name:8s}: メモリ ~{est['memory_mb']:.0f}MB, 時間 ~{est['timeout']:.0f}秒")
    print()

    # 実行するスクリプト
    scripts = [
        ("11_process_for.py", "For-Loop", "for"),
        ("12_process_pandas.py", "Pandas", "pandas"),
        ("13_process_sparks.py", "Spark", "spark"),
    ]

    results = {}

    for script_path, script_name, est_key in scripts:
        if not os.path.exists(script_path):
            print(f"⚠ {script_path} が見つかりません")
            results[script_name] = "スキップ"
            continue

        # 推定値から制限を設定（余裕を持たせる）
        memory_limit = int(estimates[est_key]["memory_mb"] * 1.5)
        timeout = int(estimates[est_key]["timeout"] * 1.5)

        monitor = ProcessMonitor(
            timeout=timeout,
            memory_limit_mb=memory_limit
        )

        success = monitor.run(script_path, script_name)
        results[script_name] = "✓ 成功" if success else "❌ 失敗"

        # 失敗した場合、次のスクリプトを実行するか確認
        if not success:
            response = input(f"\n次のスクリプトを実行しますか？ (y/n): ").strip().lower()
            if response != 'y':
                print("実行を中断します")
                break

    # サマリー
    print(f"\n{'='*60}")
    print("実行結果サマリー")
    print('='*60)
    for name, status in results.items():
        print(f"{name:20s}: {status}")
    print('='*60)


if __name__ == "__main__":
    main()