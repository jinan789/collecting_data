import os

for i in range(20):
    print(i)
    cur_path = '/mnt/muhui/kernel_cve/L' + str(i)
    if os.path.exists(cur_path):
        print('skipped', str(i))
        continue
    command = 'cp -R ../linux/ /mnt/muhui/kernel_cve/L'  + str(i)
    os.system(command)