#!/usr/bin/env python
from src.primitive_db import engine

def main():
    print('DB project is running!')
    engine.run()


if __name__ == '__main__':
    main()