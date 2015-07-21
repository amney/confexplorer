import argparse
import json

import requests
from flask import Flask, render_template

app = Flask(__name__, template_folder='')


def apic_login(session, apic_url, apic_username, apic_password):
    data = {
        "aaaUser": {
            "attributes": {
                "name": apic_username,
                "pwd": apic_password
            }
        }
    }
    session.post(url=apic_url + "/api/aaaLogin.json", data=json.dumps(data), verify=False)


def get_top_level_objects(session, apic_url):
    r = session.get(url=apic_url + "/api/node/mo/uni.json?query-target=children")
    return r.json()['imdata']


def get_config_tree(session, apic_url, uni):
    """
        Get the entire configuration tree in JSON format from the APIC

        We must create a set of the top level objects under polUni as
        the APIC does not support the rsp-subtree=full query param
    """

    top_level_classes = set()
    config = {}

    for mo in uni:
        key = mo.keys()[0]
        top_level_classes.add(key)

    for cls in top_level_classes:
        r = session.get(
            url=apic_url + "/api/node/class/{}.json?rsp-subtree=full&rsp-prop-include=config-only".format(cls))
        if r.ok:
            config[cls] = dict(children=[])
            config[cls]['children'] = r.json()['imdata']
    return config


def _process_children(parent, children, depth=0):
    # Have we hit recursion limit?
    if depth >= MAX_DEPTH:
        return

    for klass in children:

        for cls, data in klass.items():
            """
                Try get some sensible name from the object, if not try get the DN.
                If the name turns out to be empty use the DN. If that's not possible
                skip this object entirely so we don't dispaly a blank circle.
            """
            try:
                name = data['attributes']['name']
            except KeyError:
                try:
                    name = data['attributes']['dn']
                except KeyError:
                    continue
            if not name:
                try:
                    name = data['attributes']['dn']
                except KeyError:
                    continue

            # Create this MO and then recurse all children objects
            mo = dict(name=name, size=len(name), attributes=data['attributes'], children=[])
            try:
                _process_children(mo['children'], data['children'], depth=depth + 1)
            except KeyError:
                pass

            # Add this MO into the right parent class bucket
            for parent_cls in parent:
                if parent_cls['name'] == cls:
                    parent_cls['children'].append(mo)
                    break
            else:
                parent.append(dict(id=1, name=cls, size=1, children=[mo]))


def format_config_tree(config):
    fmt_config = {"name": "APIC", "children": []}

    for cls, data in config.items():
        _process_children(fmt_config['children'], data['children'], 0)

    return fmt_config


@app.route('/config.json')
def config_json():
    session = requests.Session()

    apic_login(session, url, login, password)

    uni = get_top_level_objects(session, url)
    config_tree = get_config_tree(session, url, uni)
    formatted_config_tree = format_config_tree(config_tree)

    return json.dumps(formatted_config_tree, indent=4)


@app.route('/')
def home():
    return render_template('explorer.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ACI Configuration Visualisers')
    parser.add_argument('-u', '--url',
                        required=True,
                        help='APIC IP address.')
    parser.add_argument('-l', '--login',
                        required=True,
                        help='APIC login ID.')
    parser.add_argument('-p', '--password',
                        required=True,
                        help='APIC login password.')
    parser.add_argument('-d', '--depth',
                        default=2,
                        type=int,
                        help='Maximum config recursion depth. DEFAULT=2')
    parser.add_argument('--host',
                        default='127.0.0.1',
                        help='Address Flask server listens on. DEFAULT=127.0.0.1')
    parser.add_argument('--port',
                        default=5000,
                        type=int,
                        help='Port Flask server listens on. DEFAULT=5000')

    args = parser.parse_args()

    url = args.url
    login = args.login
    password = args.password
    MAX_DEPTH = args.depth
    host = args.host
    port = args.port

    app.run(debug=True, host=host, port=port)
