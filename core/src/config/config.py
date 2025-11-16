import configparser
import json
import os

# config.iniへのパスを解決 (このファイルの3階層上にconfig.iniがあると仮定)
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.ini'))

config = configparser.ConfigParser()
if not config.read(config_path, encoding='utf-8'):
    raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

# 取引所の設定を読み込む
EXCHANGES = {}
for section in ['gmo', 'bitbank']:
    if section in config:
        EXCHANGES[section] = {
            'api_endpoint': config.get(section, 'api_endpoint'),
            'fee_rate': config.getfloat(section, 'fee_rate')
        }

# 監視対象の通貨ペアを読み込む
TARGET_PAIRS = {}
if 'target_pairs' in config:
    for key, value in config.items('target_pairs'):
        try:
            # JSON文字列を辞書に変換
            TARGET_PAIRS[key.upper()] = json.loads(value)
        except json.JSONDecodeError:
            print(f"警告: 'target_pairs'セクションのキー'{key}'の値の解析に失敗しました。")


# その他の設定を読み込む
LOG_LEVEL = config.get('logging', 'level', fallback='INFO')
