**Im using Google just as versioning tool. Currently, project is in early stage and HIGHLY EXPERIMENTAL. You can watch sources, but please don't run script on production servers. Using this software is on your own risk.**

This application helps with tracking bad exit nodes on Tor network.

Process of bad nodes detection is easy:

  * **1.Phase** - find many different links on Internet
  * **2.Phase** - ask every exit node on Tor network to give these links.
  * **3.Phase** - compare results (based on detailed analysis of content) of the same content given from different exit nodes.

Difference in content isn't bad in general. Web pages contains dynamic fragments like time, news etc. Script is comparing TENDENCY in changes between given contents. When every exit nodes (not counting one) returns the same content, we can expect that the one node is problematic (a little bit simplified).

Script uses plugin architecture, so it is possible to add more protocol and filetype handlers (ISO files, SMTP transfers).


---

More about Tor network and exit nodes: http://www.torproject.org