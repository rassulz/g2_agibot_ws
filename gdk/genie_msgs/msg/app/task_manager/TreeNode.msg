uint32      uid

uint8 TYPE_UNDEFINED   = 0
uint8 TYPE_ACTION      = 1
uint8 TYPE_CONDITION   = 2
uint8 TYPE_CONTROL     = 3
uint8 TYPE_DECORATOR   = 4
uint8 TYPE_SUBTREE     = 5

uint8       type
string      registration_id
string      name
string      path
uint32[]    children_uid

uint8 STATUS_UNDEFINED   = 0
uint8 STATUS_IDLE    = 1
uint8 STATUS_RUNNING = 2
uint8 STATUS_SUCCESS = 3
uint8 STATUS_FAILURE = 4
uint8 STATUS_SKIPPED = 5

uint8       status

