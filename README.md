<article class="markdown-body entry-content p-3 p-md-6" itemprop="text">
<h1>
    <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-.98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z"></path></svg>Practica 3
</h1>
<h2>
    <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-.98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z"></path></svg>Table of Contents
</h2>
<ul>
<li><a href="#introduction">Introduction</a></li>
<li><a href="#testing">Testing</a></li>
<li><a href="#license">License</a></li>
<li><a href="#usage">Usage</a></li>
<li><a href="#documentation">Documentation</a></li>
<li><a href="#requirements">Requirements</a></li>
<li><a href="#news">News</a></li>
<li><a href="#future">Future</a></li>
</ul>
<h2><a id="user-content-introduction" class="anchor" aria-hidden="true" href="#introduction"></a>Introduction</h2>
<p>The program is a client which purpose is to send and receive real-time videos from a webcam. By calling one of your friends you will be able to see each other 
through an unresizable window of 640x480. Many features are still to be implemented and are described in <a href="#future">this</a> section.<br/>
Launching the app you will attend a first window dedicated to logging, here two options will be proposed:<br/>
<ul><li>Log manually: you shall enter your credentials (username, password)</li>
<li>Log from file: you shall enter the path of a text file from which the program will pull out the info (username, passsword, receiving port)</li></ul>
Then you will reach the main window, composed of different elements which you can find more details in the [wiki](../../wikis/Home) section. This layout will allow you for instance to get the list
of registered users, to log out from the app, to quit the app and of course to start a call. All of these steps are detailed in sections below.
</p>
<h2><a id="user-content-testing" class="anchor" aria-hidden="true" href="#testing"></a>Testing</h2>
<p>To fully appreciate the functionalities provided by this program the user must have a friend or a colleague connected at the same time on another 
computer (see <a href="#requirements">Requirements</a>). In case you don't have the ability to call someone or you just want to see yourself in a mirror you can follow 
these few steps to launch the client twice and therefore simulate a call. First launch the program from two different console windows (see <a href="#testing">Testing</a>). Then log in 
from file or manually, but in any case do not log with same username because the behaviour would be undefined. Here you should observe two similar windows with a slight difference in the top left corner, the username is not the same.
Finally you should be able to pick the name you entered in the other client in the list located on the left of the screen. Wait a few seconds...on the other client 
should appear a small windows saying that you (well the other you) is receiving a call, you will be able ti accept or decline this invitaion by pressing
one of the two buttons. Be aware that a timer of 30 seconds is started when sending a call request after which the call is considered as missed by the sender client. Another 
relevant info is that calling a user is "blocking" which means that your client will be inactive from the moment you press "Call" until a response is received.<br/>
Four responses may be expected, the call can be accepted of course and can be denied as well. If the other side is not connected then you will see a message indicating that called user is not available
in the second part of the statusbar. If the other side is already in a call then you will receive a message explaining that he or she is currently busy. The details
of the exchanged messages between clients are provided in the wiki. During a call you will be able to pause, resume or hang up through buttons located at the bottom
of the main window.</p>
<h2><a id="user-content-license" class="anchor" aria-hidden="true" href="#license"></a>License</h2>
<p><b>Attribution</b> — You must give appropriate credit, provide a link to the license (see file LICENSE), and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.<br/>
<b>NonCommercial</b> — You may not use the material for commercial purposes.<br/>
<b>No additional restrictions</b> — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.</p>
<h2><a id="user-content-usage" class="anchor" aria-hidden="true" href="#usage"></a>Usage</h2>
1. Download all the files as a .zip in a safe location<br/>
2. Decompress it and open 2 Terminal windows from the folder<br/>
3. Execute <i>python3 practica3_client.py</i> in both windows<br/>
4. Log in (manually or through a configuartion file)<br/>
5. In one of the instances select the other client username by clicking once in the list<br/>
6. Press call and wait a few seconds<br/>
7. On the other side accept the call via the newly printed window<br/>
8. At any moment press Hang up, or Pause the call<br/>
9. Afterwards it is posible to Quit or Log out<br/>

<br/>Files included:
<ul>
<li><b>README.md</b> - The file you are reading</li>
<li><b>practica3_client.py</b> - Ihe program itself</li>
<li><b>config.txt</b> - An example of a configuration file supported by the client</li>
<li><b>config2.txt</b> - Same as previous one but with different username and port</li>
<li><b>calls.py</b> - A python file that provides fonctions and stuff related to the calls</li>
<li><b>images</b> - Folder that stores the images needed by the client, at this time there is only a backrgound with message WELCOME</li>
</ul>
<h2><a id="user-content-documentation" class="anchor" aria-hidden="true" href="#documentation"></a>Documentation</h2>
In case you need any further information please take a look at the wiki:<br/>
1. [Functionalities](../../wikis/Functionalities)<br/>
2. [Functions](../../wikis/Functions)<br/>
3. [Usage & Errors](../../wikis/Usage-&-Errors)

<br/>
<h2><a id="user-content-requirements" class="anchor" aria-hidden="true" href="#requirements"></a>Requirements</h2>
This program has been tested on MacOS with python3.8 and Ubuntu 16.04 with python3.6. No guarantee is provided on other operating systems or python versions.
Moreover, the client uses a few packages that you will need to install:
<ul>
<li><b>Tk</b> $ sudo apt install python3-pil.imagetk python3-tk python3-numpy python-imaging-tk</li>
<li><b>appJar</b> $ pip3 install appjar</li>
<li><b>OpenCV</b> $ sudo apt install python-opencv</li>
<li><b>Camera</b> a working webcam directly linked to the computer</li>
</ul>
<h2><a id="user-content-news" class="anchor" aria-hidden="true" href="#news"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-.98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z"></path></svg></a>News</h2>
<ul>
<li>18/05: Done everything I could</li>
<li>18/05: Implemented <b>statusbar</b></li>
<li>18/05: Improved <b>Log in</b> window</li>
<li>18/05: Program is able to print whenever a wrong configuration file is passed</li>
<li>18/05: Program is able to print whenever a wrong password is passed</li>
<li>18/05: <b>Log out</b> works</li>
<li>18/05: <b>Pause, Resume</b> and <b>Hang up</b> work</li>
<li>18/05: Calls via <b>UDP</b> and control messages via <b>TCP</b> work</li>
<li>18/05: Calls are possible <b>without sound</b></li>
<li>18/05: Program is able receive the list of users <b>entirely</b>, no size limit of list of registered users</li>
<li>01/05: Added .gitignore and created <b>Calls</b> library</li>
<li>30/04: Done refresh functionality, allows user to refresh the list of registered users via a button named 'REFRESH'</li>
<li>27/04: Almost one <b>GUI</b></li>
<li>27/04: Done <b>Log manually</b></li>
<li>27/04: Created <b>securebox_client.py</b></li>
<li>27/04: Created <b>README</b></li>

*Note that this chronology is not totally exact since I did not updated on git all the steps especially in May
</ul>
<h2><a id="user-content-future" class="anchor" aria-hidden="true" href="#future"></a>Future</h2>
I plan to keep working a bit on this project for fun on my spare time. It is really interesting to develop this kind of software and I detail here the next few improvements.
Note that many of them are not implemented yet for a lack of time, and not for a lack of python knowledge (even though some of them yes). The difficulty of each task is written between
parenthesis.
<ul>
<li>Add sound (difficult)</li>
<li>Overlay a small window with the user self face (medium)</li>
<li>Add a bar on top of the video section to select the quality in real time (easy)</li>
<li>Use TCP instead of UDP to transfer frames (medium)</li>
<li>Change background back after a call is terminated (easy)</li>
</ul>
</article>