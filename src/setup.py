from setuptools import find_packages, setup

package_name = 'robotic_musician'

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
    maintainer='student',
    maintainer_email='sulliwj0@sewanee.edu',
    description='A robotic musician that can follow the conducting gestures of a user and play music in time.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gesture = robotic_musician.gesture:main',
            'music = robotic_musician.music:main',
        ],
    },
)
