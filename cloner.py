for i in range(20):
    cur_path = '/mnt/muhui/kernel_cve/L' + str(i)
    if os.path.exists(cur_path):
        continue
    command = 'cp -R ../linux/ /mnt/muhui/kernel_cve/L'  + str(i)
    os.system(command)