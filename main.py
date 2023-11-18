import yaml

def get_input(prompt, required=True):
    """Get user input with a prompt. Optionally make input required."""
    while True:
        value = input(prompt)
        if value or not required:
            return value
        else:
            print("This field is required.")

def get_yes_no(prompt):
    """Get a yes/no answer from the user."""
    while True:
        value = input(prompt + " (yes/no): ").lower()
        if value in ["yes", "no"]:
            return value == "yes"
        else:
            print("Please answer 'yes' or 'no'.")

def get_database_details():
    """Get database details from the user."""
    db_host = get_input("Enter the database host address: ")
    db_port = get_input("Enter the database port: ")
    db_username = get_input("Enter the database username: ")
    db_password = get_input("Enter the database password: ")
    db_name = get_input("Enter the database name: ")
    return {
        "db_host": db_host,
        "db_port": db_port,
        "db_username": db_username,
        "db_password": db_password,
        "db_name": db_name
    }

def get_proxy_details():
    """Get proxy details from the user."""
    proxy_type = get_input("Enter the type of reverse proxy (e.g., 'nginx', 'traefik', 'cloudflare'): ")
    if proxy_type.lower() != "cloudflare":
        proxy_host = get_input("Enter the proxy host address: ", required=False)
        proxy_port = get_input("Enter the proxy port: ", required=False)
    else:
        proxy_host = proxy_port = None
    return {
        "proxy_type": proxy_type,
        "proxy_host": proxy_host,
        "proxy_port": proxy_port
    }

def generate_docker_compose(use_db, db_details, use_proxy, proxy_details):
    """Generate the Docker Compose file."""
    compose = {
        "version": "3.8",
        "services": {
            "guacamole": {
                "image": "guacamole/guacamole",
                "ports": ["8080:8080"],
                "environment": {
                    "GUACD_HOSTNAME": "guacd",
                    "MYSQL_HOSTNAME": db_details["db_host"] if use_db else "mysql",
                    "MYSQL_DATABASE": db_details["db_name"] if use_db else "guacamole_db",
                    "MYSQL_USER": db_details["db_username"] if use_db else "guacamole_user",
                    "MYSQL_PASSWORD": db_details["db_password"] if use_db else "guacamole_password"
                },
                "depends_on": ["guacd"]
            },
            "guacd": {
                "image": "guacamole/guacd"
            }
        }
    }

    if not use_db:
        compose["services"]["mysql"] = {
            "image": "mysql",
            "environment": {
                "MYSQL_ROOT_PASSWORD": "guacamole_password",
                "MYSQL_DATABASE": "guacamole_db",
                "MYSQL_USER": "guacamole_user",
                "MYSQL_PASSWORD": "guacamole_password"
            }
        }

    if use_proxy and proxy_details["proxy_type"].lower() != "cloudflare":
        compose["services"][proxy_details["proxy_type"]] = {
            "image": proxy_details["proxy_type"],
            "ports": [f"{proxy_details['proxy_port']}:80"]
        }

    return yaml.dump(compose, sort_keys=False)

def main():
    """Main function to run the script."""
    use_db = get_yes_no("Do you have an existing RDBMS system for Guacamole? (yes/no)")
    db_details = get_database_details() if use_db else {}

    use_proxy = get_yes_no("Do you want to proxy the Guacamole web service? (yes/no)")
    proxy_details = get_proxy_details() if use_proxy else {}

    docker_compose_yaml = generate_docker_compose(use_db, db_details, use_proxy, proxy_details)
    with open('docker-compose.yml', 'w') as file:
        file.write(docker_compose_yaml)

    print("Docker Compose file generated successfully.")

if __name__ == "__main__":
    main()
