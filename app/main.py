#!/usr/bin/env python3

print("Creating hello_world.txt...")

with open("/app/hello_world.txt", "w") as f:
    f.write("Hello from Docker!\n")

print("File created successfully!")
print("Check your host machine at ~/docker/obsidian-enhanced/app/hello_world.txt")
