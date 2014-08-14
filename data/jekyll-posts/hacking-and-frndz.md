  

## Learning to Hack with Frndz

### 20 Apr 2014

Each week at Cookies and Code, students split up into small groups to explore areas of technology that catch their fancy. This week, one such group was the sensationally titled &#8220;Hacking and Frndz&#8221; (so called because &#8220;hacking&#8221; is a more exciting term than &#8220;security&#8221; and because [real hackers hate vowels](https://en.wikipedia.org/wiki/Leet)). While ADI typically uses the word &#8220;hack&#8221; in a constructive sense to denote innovative creations, this group focused on the other, darker meaning: exploiting security flaws in applications to gain illicit access.

Information security is a critical skill for anyone who wants to publish a web app or run a server of any kind on the internet. There will always be malicious users out there who will take advantage of bugs in your application, as recent news about [Heartbleed](https://en.wikipedia.org/wiki/Heartbleed) and the [NSA](https://en.wikipedia.org/wiki/Tailored_Access_Operations) demonstrates. The best way to defend against these hackers is to think like one. This involves understanding common classes of attacks as well as adopting the mindset of a hacker. In general, exploitation is done by probing boundaries and feeding unexpected input to the program in question. Hackers don&#8217;t break the rules of an application; they understand them and take advantage of technicalities.

The &#8220;Hacking and Frndz&#8221; group, a handful of security-curious individuals, isn&#8217;t about making money or performing internet vandalism. Rather, they seek to understand attacks on web applications and other programs in order to better defend against them. Each week, they learn about a specific type of attack. For now, the group focuses on web applications by using [Damn Vulnerable Web Application](http://www.dvwa.co.uk/), an intentionally exploitable web application perfect for educational exercises. As the leader of &#8220;Hacking and Frndz, &#8221; I packaged DVWA for [Vagrant](http://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/), making it a quick, easy, and safe (for obvious reasons, running a vulnerable web application directly on your computer without some sort of virtual sandbox is a bad idea) process to get a copy up and running. For those interested in following along at home, the repository can be found [here](https://github.com/znewman01/VagrantDVWA), with instructions in the `README.md` file. This week, the group learned about [cross-site scripting](https://en.wikipedia.org/wiki/Cross-site_scripting) (XSS) attacks which can lead to in-browser security issues.

The members of &#8220;Hacking and Frndz&#8221; (a fluid set, since each Cookies and Code allows attendees to join any group that catches their eye that week) have had a lot of fun learning about how to exploit web apps. A few have identified vulnerabilities in their own projects that they have since fixed, and many mentioned an interest in learning more about security outside of the group. &#8220;Hacking and Frndz&#8221; meets most weeks at Cookies and Code, so feel free to stop by and check it out!

- Zachary Newman

  
