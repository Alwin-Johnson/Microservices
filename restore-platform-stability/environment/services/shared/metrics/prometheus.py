from prometheus_client import Counter, Histogram, Gauge

# HTTP Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency', 
    ['method', 'endpoint']
)
ERROR_COUNT = Counter(
    'http_errors_total', 
    'Total HTTP errors', 
    ['method', 'endpoint', 'error_type']
)

# Business Histograms
CHECKOUT_LATENCY = Histogram(
    'checkout_duration_seconds', 
    'Checkout workflow latency'
)
PAYMENT_LATENCY = Histogram(
    'payment_processing_duration_seconds', 
    'Payment processing latency'
)

# HTTP Client (Outbound) Metrics
OUTBOUND_REQUEST_COUNT = Counter(
    'outbound_http_requests_total',
    'Total outbound HTTP requests',
    ['method', 'target_url', 'status_code']
)
OUTBOUND_REQUEST_LATENCY = Histogram(
    'outbound_http_request_duration_seconds',
    'Outbound HTTP request latency',
    ['method', 'target_url']
)

# Database / Redis Pool Metrics
DB_CONNECTIONS_IN_USE = Gauge(
    'db_connections_in_use',
    'Database connections currently in use'
)
REDIS_CONNECTIONS_IN_USE = Gauge(
    'redis_connections_in_use',
    'Redis connections currently in use'
)
