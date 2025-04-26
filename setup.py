
from setuptools import setup, find_packages                                                   
                                                                                              
setup(                                                                                        
    name="zai",                                                                        
    version="1.0.0",                                                                          
    packages=find_packages(),                                                                 
    entry_points={                                                                            
        'console_scripts': [                                                                  
            'zai = zai.__main__:main'                                           
        ]                                                                                     
    }                                                                                         
)                                                                                             
    
