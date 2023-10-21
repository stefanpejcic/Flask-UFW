from flask import Flask, render_template, request, g, jsonify, session, url_for, flash, redirect
import json


app = Flask(__name__)
app.debug = True
app.secret_key = 'Da168IGFs2F'
app.template_folder = 'templates'






# HOME PAGE
@app.route('/')
def firewall_settings():
    firewall_rules, firewall_status = get_firewall_rules()
    print(firewall_status)

    return render_template('firewall_settings.html', title="Firewall", firewall_rules=firewall_rules, firewall_status=firewall_status)


@app.route('/settings/firewall/delete-rule/<int:rule_number>', methods=['POST'])
def delete_firewall_rule(rule_number):
    try:
        ufw_command = ['ufw', 'delete', str(rule_number)]
        print(f"Executing command: {' '.join(ufw_command)}")

        # Use subprocess.run to automatically answer 'yes' to prompts
        process = subprocess.run(ufw_command, input='yes\n', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        if process.returncode == 0:
            print(f"Command output: {process.stdout}")
            return jsonify({'message': 'Rule deleted successfully'})
    except subprocess.CalledProcessError as e:
        print(f"Command returned non-zero exit code: {e.returncode}")
        return jsonify({'message': f'Error deleting rule: {e.stderr}'}, 500)
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return jsonify({'message': 'Command timed out'}, 500)

    return jsonify({'message': 'An unknown error occurred'}, 500)



@app.route('/settings/firewall/add-rule', methods=['POST'])
def add_firewall_rule():
    action = request.form.get('action')  # 'allow' or 'deny'
    input_data = request.form.get('input_data')

    try:
        if action == 'allow':
            if input_data.isdigit():
                # Format as 'ufw allow <port>/tcp'
                ufw_command = ['ufw', 'allow', f'{input_data}/tcp']
            else:
                # Format as 'ufw allow from <IP>'
                ufw_command = ['ufw', 'allow', 'from', f'{input_data}']
        elif action == 'deny':
            if input_data.isdigit():
                # Format as 'ufw deny <port>/tcp'
                ufw_command = ['ufw', 'deny', f'{input_data}/tcp']
            else:
                # Format as 'ufw deny from <IP>'
                ufw_command = ['ufw', 'deny', 'from', f'{input_data}']
        else:
            return jsonify({'message': 'Invalid action'}, 400)

        print(ufw_command)
        # Execute the ufw command
        process = subprocess.run(ufw_command, input='yes\n', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        if process.returncode == 0:
            return jsonify({'message': 'Rule added successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'message': f'Error adding rule: {e.stderr}'}, 500)
    except subprocess.TimeoutExpired:
        return jsonify({'message': 'Command timed out'}, 500)

    return jsonify({'message': 'An unknown error occurred'}, 500)



@app.route('/json/ufw-log', methods=['GET'])
def get_ufw_log():
    try:
        # Run the "tail /var/log/ufw.log" command and capture its output
        log_output = subprocess.check_output(['tail', '-25', '/var/log/ufw.log'], universal_newlines=True)
        
        # Split the output into lines
        log_lines = log_output.split('\n')
        
        # Return the log lines as a JSON response
        return jsonify({'ufw_log': log_lines})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f"Error running command: {e}"})











from flask import Flask, redirect, url_for, render_template, flash
from subprocess import Popen, PIPE

@app.route('/service/<action>/<service_name>')
def manage_service(action, service_name):
    # Define a list of allowed services
    allowed_services = ['ufw']

    # Define a dictionary to map service actions to shell commands
    service_actions = {
        'start': 'start',
        'restart': 'restart',
        'stop': 'stop'
    }

    if action not in service_actions:
        flash('Invalid action: {}'.format(action), 'error')
        return redirect(url_for('firewall_settings'))

    if service_name not in allowed_services:
        flash('Invalid service: {}'.format(service_name), 'error')
        return redirect(url_for('firewall_settings'))

    # Construct the shell command to manage the service
    command = ['sudo', 'service', service_name, service_actions[action]]

    try:
        # Execute the shell command
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            flash('Service {} {}ed successfully'.format(service_name, action), 'success')
        else:
            flash('Error {}ing service {}: {}'.format(action, service_name, stderr.decode()), 'error')
    except Exception as e:
        flash('Error executing command: {}'.format(str(e)), 'error')

    return redirect(url_for('firewall_settings'))


import subprocess

def get_firewall_rules():
    try:
        # Use a single subprocess call to run both 'ufw status numbered' and 'jc --ufw'
        cmd = 'ufw status numbered | jc --ufw'
        result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        data = json.loads(result)

        # Extract the rules from the JSON data
        firewall_rules = data.get('rules', [])
        firewall_status = data.get('status', '')

        return firewall_rules, firewall_status

    except subprocess.CalledProcessError as e:
        return [{'error': str(e)}]


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'strogosecret'
    app.run(debug=True, host='0.0.0.0', port=5000)
