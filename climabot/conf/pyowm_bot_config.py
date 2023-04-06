from pyowm.commons.enums import SubscriptionTypeEnum

WEATHER_DEFAULT_CONFIG = {
    'subscription_type': SubscriptionTypeEnum.FREE,
    'language': 'es',
    'connection': {
        'use_ssl': True,
        'verify_ssl_certs': True,
        'use_proxy': False,
        'timeout_secs': 5,
        'max_retries': None
    },
    'proxies': {
        'http': 'http://user:pass@host:port',
        'https': 'socks5://user:pass@host:port'
    }
}
