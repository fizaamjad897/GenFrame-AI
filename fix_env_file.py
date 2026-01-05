import os

def fix_env_file():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    seen_secret_key = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
            
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\" ")
            
            if key == "SECRET_KEY":
                if not seen_secret_key:
                    # First one is usually Storage/Digital Ocean
                    new_lines.append(f"DO_SECRET_KEY={value}\n")
                    seen_secret_key = True
                else:
                    # Second one is usually JWT
                    new_lines.append(f"JWT_SECRET={value}\n")
            elif key == "ACCESS_KEY_ID":
                new_lines.append(f"DO_ACCESS_KEY_ID={value}\n")
            elif key == "SPACEREGION":
                # Force correct region for SFO3
                new_lines.append(f"SPACEREGION=sfo3\n")
            else:
                new_lines.append(f"{key}={value}\n")
        else:
            new_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    print("✅ .env file cleaned and renamed! (Renamed duplicate SECRET_KEY to DO_SECRET_KEY and JWT_SECRET)")

if __name__ == "__main__":
    fix_env_file()
