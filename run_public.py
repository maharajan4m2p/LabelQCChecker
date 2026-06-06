import os

from pyngrok import ngrok

from app import app


def main():
    port = int(os.environ.get("PORT", 5000))
    public_url = ngrok.connect(port, bind_tls=True).public_url
    print("Public URL:", public_url)
    print("Running Flask on 0.0.0.0:%s" % port)
    print("Press Ctrl+C to stop.")
    try:
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    finally:
        ngrok.disconnect(public_url)


if __name__ == "__main__":
    main()
