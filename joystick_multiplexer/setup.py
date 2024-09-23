from setuptools import find_packages, setup

package_name = 'joystick_multiplexer'

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
    maintainer='adam',
    maintainer_email='01149057@pw.edu.pl',
    description='Multiplexer joysticka dla ROS2',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
    'console_scripts': [
        'joy_multiplexer = joystick_multiplexer.joystick_multiplexer:main'],},)
