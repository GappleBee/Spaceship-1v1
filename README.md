# Spaceship 1v1

This project was mainly for education purposes, starting with the asset folder and a short playthrough of the final game (https://youtu.be/jO6qQDNa2UY). This is just an implementation of that final game though there are a few optimisations that are used in this implementation:
1. Double buffering - Increases performance
2. Using .convert() on certain images - Significantly increases performance
3. Killing dead sprites - Prevents memory leaks
4. Presetting audio settings - Improves sound quality
5. Performing operations like (x + y) / 2 instead of x / 2 + y / 2 - Increases performance by reducing the number of calculations needed

Also, to run this you will need to install the PyGame module.
