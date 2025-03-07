from setuptools import find_packages, setup

package_name = 'firo_joy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gabriel Brzeziński',
    maintainer_email='gabriel@gabrielb.dev',
    description='Joy nodes for controlling FIRO robots',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
    'console_scripts': [
        'joy_crossbar_switch = firo_joy.joy_crossbar_switch:main'],},)
