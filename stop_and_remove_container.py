from docker_manager import stop_and_remove_container

# Replace 'container_id_here' with the actual container ID
result = stop_and_remove_container('1')
print("Container stopped and removed:", result)
