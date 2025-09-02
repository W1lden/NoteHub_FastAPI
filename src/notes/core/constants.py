# Models
TITLE_MAX_LEN = 255
NAME_MAX_LEN = 100

# Auth
MIN_PASSWORD_LEN = 7
JWT_LIFETIME_SEC = 3600

# Redis
REDIS_CHAT_HISTORY_KEY = (
    "chat:history"  # Redis key where chat messages are stored
)
HISTORY_LAST_N_MESSAGES = (
    20  # Number of messages loaded for a new user when joining
)
HISTORY_MAX_SAVE_LEN = (
    1000  # Maximum number of messages stored in Redis (older ones are deleted)
)
LIST_END = (
    -1
)  # Index of the last element in the list (always the newest message)
