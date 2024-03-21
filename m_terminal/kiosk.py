import json
from flask import Flask, render_template, send_from_directory


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # ips are found in ip_config.json
    ip_vals = {k: "http://" + v  for k,v in ips.items()  if isinstance(v, str)}
    return render_template("kiosk_tabs.html", ips=ip_vals)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", 'server_favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5501)
