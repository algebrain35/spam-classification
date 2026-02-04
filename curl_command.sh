curl -X 'POST' \
  'http://127.0.0.1:8000/batch' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "body": "Dear User,\n\nOur systems have detected an unusual login attempt to your account from an unrecognized device in a different country.\n\nLogin Details:\n\n    Location: Moscow, Russia\n\n    IP Address: 185.151.242.10\n\n    Device: Linux / Chrome\n\nIf this was not you, please click the button below immediately to secure your account and verify your identity. Failure to complete this verification within 24 hours will result in a permanent suspension of your account to prevent unauthorized access.\n\n[ Secure My Account Now ]\n\nThank you for helping us keep your account safe.\n\nThe Security Team",
    "sender": "normanjames@gmail.com",
    "subject": "Security Alert"
  },
  {
    "body": "Meeting update",
    "sender": "hr@test.com",
    "subject": "deeznuts"
  }
]'
