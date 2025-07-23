import sentry_sdk
from flask import Flask

# Initialize Sentry with your DSN
sentry_sdk.init(
    dsn="https://a4a1e2fb28becfe6aa44ef0b93f8ed8e@o4509702640697344.ingest.us.sentry.io/4509702645350400",
    send_default_pii=True,
)

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World! Sentry test app is running.</p>"


@app.route("/test-error")
def test_error():
    """Route to test Sentry error reporting"""
    1 / 0  # This will raise a ZeroDivisionError
    return "<p>This should not be reached</p>"


@app.route("/test-message")
def test_message():
    """Route to test Sentry message capture"""
    sentry_sdk.capture_message("Test message from Sentry test app")
    return "<p>Test message sent to Sentry</p>"


if __name__ == "__main__":
    print("Sentry Test App")
    print("Visit /test-error to trigger an error")
    print("Visit /test-message to send a test message")
    app.run(host="0.0.0.0", port=5001, debug=True)
