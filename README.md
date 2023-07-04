# Render World - Interface para visualização 3D em Python com Tkinter

![alt text](https://github.com/JulioCalandrin/RenderWorld/blob/main/Screenshot.png/?raw=true)

Este trabalho foi desenvolvido para a disciplina de Computação Gráfica - SEL0377, seguindo o tema de realidade virtual.
Nele buscamos realizar a conexão do computador com um celular por meio de uma porta serial via Bluetooth, onde um aplicativo coleta dados do gisroscópio interno do smartphone e os enviava para o software RenderWolrd, a fim de manipular o arquivo .obj sendo visualizado.

Foi utilizado o Tkinter como ferramenta gráfica, onde uma canvas é utilizada para receber as formas renderizadas. Infelizmente os algortimos utilizados não foram otimizados, portanto estamos limitados a utilizar objetos mais simples. Objetos mais complexos, principalmente com curvas, tornam o processo de renderização muito custoso por elevar o numero de pontos a serem processados, limitando a velocidade de atualização dos frames.
Para executá-lo, instale as dependências listadas no requirements.txt e execute o arquivo RenderWorld.py

# Detalhe da comunicação bluetooth

Foi utilizada uma porta serial via bluetooth no windows. Para isso, adicionei manualmente uma nova porta COM nas configurações de bluetooth no painel de controle. Infelizmente não testei no Linux.

# Referencias:

As funcões de manipulação de arquivos .obj e de transformações 3D foram baseadas no trabalho de: https://github.com/Rad-hi/3D-Rendering-Desktop-App

Note que no vídeo de demonstração disponível no link acima, vemos um modelo grande, com muito pontos sendo apresentado com tranquilidade. Quero investigar o que causou uma perda tão grande de performance na minha aplicação, possivelmente causado pelo uso do tema Azure aplicado sobre o TKinter.




