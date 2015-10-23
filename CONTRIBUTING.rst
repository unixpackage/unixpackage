Contributing
============

Hi and thanks for showing interest in helping out with unixpackage!

Here's a number of things you can do to help. Note that you *don't*
have to be a developer to help:

#1 Create and upload working and fully upgraded vagrant boxes
-------------------------------------------------------------

Currently unixpackage is largely limited by the ability to test
it on multiple platforms using vagrant. The more vagrant boxes
out there the more platforms I can get it to work on.

If you create a vagrant box for your platform raise an issue,
give me the link and let me know and I'll try and make it work.

#2 Add packages
---------------

It's really easy to add packages. Just add a snippet of JSON with the
package equivalents on different platforms and submit a pull request.

Look at the examples to get a feel.

You can search for equivalent packages using the websites mentioned
in the README.

#3 Add packages for distros not currently supported
---------------------------------------------------

If you go through each of the packages and add packages for another
package manager or distro (e.g. macports or mandriva or gentoo)
then I'll try my best to make it work.


#4 Submit a pull request to add a feature or fix a bug
------------------------------------------------------

Here are some ideas for features:

* Additional linux distros and package managers.

* Ability to handle multiple package managers seamlessly - e.g. on Debian, virtualenv and node-less are installed via apt-get, whereas on the Mac, virtualenv is installed with pip and node-less is installed with npm.

* The ability to detect versions of libraries or other installed software irrespective of what package manager was used to install them, or even if a package manager was used at all (e.g. using ldconfig).

* Version handling - the ability to specify which versions of software to install or check for (e.g. calling "firefox -V" and verifying the output)

* Detect if there is a package installed which has an update.
