%define major 1
%define libname %mklibname pcap %major
%define develname %mklibname pcap -d

Summary:        A system-independent interface for user-level packet capture
Name:		libpcap
Version:	1.2.0
Release:	%mkrel 1
License:	BSD
Group:		System/Libraries
URL:		http://www.tcpdump.org/
Source0:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
Patch0:		libpcap-1.2.0-pcap-config_fix.diff
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libnl-devel
#BuildRequires:	libnl3-devel <- not yet
# for bluetooth/bluetooth.h
BuildRequires:	bluez-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Suggests: %name-doc

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package doc
Summary: Manual pages for %name
Group: Books/Other
BuildArch: noarch
Conflicts: %develname < 1.1.1-3

%description doc
This contains the manual pages documenting %{name}.

%package -n	%{libname}
Summary:	A system-independent interface for user-level packet capture
Group:          System/Libraries
Obsoletes:      %{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
Provides:       pcap = %{version}-%{release}

%description -n	%{libname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{develname}
Summary:	Static library and header files for the pcap library
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
Provides:	pcap-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname pcap -d 0}

%description -n	%{develname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

This package contains the static pcap library and its header files needed to
compile applications such as tcpdump, etc.

%prep

%setup -q -n %{name}-%{version}
%patch0 -p0

%build
export CFLAGS="%{optflags} -fPIC"

%configure2_5x \
    --enable-ipv6 \
    --enable-bluetooth

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_bindir}

%makeinstall_std

# install additional headers
install -m0644 pcap-int.h %{buildroot}%{_includedir}/
install -m0644 pcap/bluetooth.h %{buildroot}%{_includedir}/pcap/

# nuke the statis lib
rm -f %{buildroot}%{_libdir}/libpcap.a

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%doc README* CREDITS INSTALL.txt LICENSE
%{_libdir}/libpcap.so.%{major}*

%files doc
%defattr(-,root,root)
%{_mandir}/man?/*

%files -n %{develname}
%defattr(-,root,root)
%doc CHANGES TODO
%{_bindir}/pcap-config
%dir %{_includedir}/pcap
%{_includedir}/pcap/*.h
%{_includedir}/*.h
%{_libdir}/libpcap.so
