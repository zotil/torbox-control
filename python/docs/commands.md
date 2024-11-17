<a id="control-spec.txt-3"></a>

# Commands

All commands are case-insensitive, but most keywords are case-sensitive.

<a id="control-spec.txt-3.1"></a>

## SETCONF

Change the value of one or more configuration variables.  The syntax is:

```text
    "SETCONF" 1*(SP keyword ["=" value]) CRLF
    value = String / QuotedString
```

Tor behaves as though it had just read each of the key-value pairs
from its configuration file.  Keywords with no corresponding values have
their configuration values reset to 0 or NULL (use RESETCONF if you want
to set it back to its default).  SETCONF is all-or-nothing: if there
is an error in any of the configuration settings, Tor sets none of them.

Tor responds with a "250 OK" reply on success.
If some of the listed keywords can't be found, Tor replies with a
"552 Unrecognized option" message. Otherwise, Tor responds with a
"513 syntax error in configuration values" reply on syntax error, or a
"553 impossible configuration setting" reply on a semantic error.

Some configuration options (e.g. "Bridge") take multiple values. Also,
some configuration keys (e.g. for hidden services and for entry
guard lists) form a context-sensitive group where order matters (see
GETCONF below). In these cases, setting _any_ of the options in a
SETCONF command is taken to reset all of the others. For example,
if two ORListenAddress values are configured, and a SETCONF command
arrives containing a single ORListenAddress value, the new command's
value replaces the two old values.

Sometimes it is not possible to change configuration options solely by
issuing a series of SETCONF commands, because the value of one of the
configuration options depends on the value of another which has not yet
been set. Such situations can be overcome by setting multiple configuration
options with a single SETCONF command (e.g. SETCONF ORPort=443
ORListenAddress=9001).

<a id="control-spec.txt-3.2"></a>

## RESETCONF

Remove all settings for a given configuration option entirely, assign
its default value (if any), and then assign the String provided.
Typically the String is left empty, to simply set an option back to
its default. The syntax is:

```text
    "RESETCONF" 1*(SP keyword ["=" String]) CRLF
```

Otherwise it behaves like SETCONF above.

<a id="control-spec.txt-3.3"></a>

## GETCONF

Request the value of zero or more configuration variable(s).
The syntax is:

```text
    "GETCONF" *(SP keyword) CRLF
```

If all of the listed keywords exist in the Tor configuration, Tor replies
with a series of reply lines of the form:

```text
    250 keyword=value
```

If any option is set to a 'default' value semantically different from an
empty string, Tor may reply with a reply line of the form:

```text
    250 keyword
```

Value may be a raw value or a quoted string.  Tor will try to use unquoted
values except when the value could be misinterpreted through not being
quoted. (Right now, Tor supports no such misinterpretable values for
configuration options.)

If some of the listed keywords can't be found, Tor replies with a
`552 unknown configuration keyword` message.

If an option appears multiple times in the configuration, all of its
key-value pairs are returned in order.

If no keywords were provided, Tor responds with `250 OK` message.

Some options are context-sensitive, and depend on other options with
different keywords.  These cannot be fetched directly.  Currently there
is only one such option: clients should use the "HiddenServiceOptions"
virtual keyword to get all HiddenServiceDir, HiddenServicePort,
HiddenServiceVersion, and HiddenserviceAuthorizeClient option settings.

<a id="control-spec.txt-3.4"></a>

## SETEVENTS

Request the server to inform the client about interesting events.  The
syntax is:

```text
    "SETEVENTS" [SP "EXTENDED"] *(SP EventCode) CRLF
    
    EventCode = 1*(ALPHA / "_")  (see section 4.1.x for event types)
```

Any events _not_ listed in the SETEVENTS line are turned off; thus, sending
SETEVENTS with an empty body turns off all event reporting.

The server responds with a `250 OK` reply on success, and a `552
Unrecognized event` reply if one of the event codes isn't recognized.  (On
error, the list of active event codes isn't changed.)

If the flag string "EXTENDED" is provided, Tor may provide extra
information with events for this connection; see 4.1 for more information.
NOTE: All events on a given connection will be provided in extended format,
or none.
NOTE: "EXTENDED" was first supported in Tor 0.1.1.9-alpha; it is
always-on in Tor 0.2.2.1-alpha and later.

Each event is described in more detail in Section 4.1.

<a id="control-spec.txt-3.5"></a>

## AUTHENTICATE

Sent from the client to the server.  The syntax is:

```text
    "AUTHENTICATE" [ SP 1*HEXDIG / QuotedString ] CRLF
```

This command is used to authenticate to the server. The provided string is
one of the following:

```text
     * (For the HASHEDPASSWORD authentication method; see 3.21)
       The original password represented as a QuotedString.

     * (For the COOKIE is authentication method; see 3.21)
       The contents of the cookie file, formatted in hexadecimal

     * (For the SAFECOOKIE authentication method; see 3.21)
       The HMAC based on the AUTHCHALLENGE message, in hexadecimal.
```

The server responds with `250 OK` on success or `515 Bad authentication` if
the authentication cookie is incorrect.  Tor closes the connection on an
authentication failure.

The authentication token can be specified as either a quoted ASCII string,
or as an unquoted hexadecimal encoding of that same string (to avoid escaping
issues).

For information on how the implementation securely stores authentication
information on disk, see section 5.1.

Before the client has authenticated, no command other than
PROTOCOLINFO, AUTHCHALLENGE, AUTHENTICATE, or QUIT is valid.  If the
controller sends any other command, or sends a malformed command, or
sends an unsuccessful AUTHENTICATE command, or sends PROTOCOLINFO or
AUTHCHALLENGE more than once, Tor sends an error reply and closes
the connection.

To prevent some cross-protocol attacks, the AUTHENTICATE command is still
required even if all authentication methods in Tor are disabled.  In this
case, the controller should just send "AUTHENTICATE" CRLF.

(Versions of Tor before 0.1.2.16 and 0.2.0.4-alpha did not close the
connection after an authentication failure.)

<a id="control-spec.txt-3.6"></a>

## SAVECONF

Sent from the client to the server.  The syntax is:
```text
    "SAVECONF" [SP "FORCE"] CRLF
```

Instructs the server to write out its config options into its torrc. Server
returns `250 OK` if successful, or `551 Unable to write configuration
to disk` if it can't write the file or some other error occurs.

If the %include option is used on torrc, SAVECONF will not write the
configuration to disk. If the flag string "FORCE" is provided, the
configuration will be overwritten even if %include is used. Using %include
on defaults-torrc does not affect SAVECONF. (Introduced in 0.3.1.1-alpha.)

See also the "getinfo config-text" command, if the controller wants
to write the torrc file itself.

See also the "getinfo config-can-saveconf" command, to tell if the FORCE
flag will be required. (Also introduced in 0.3.1.1-alpha.)

<a id="control-spec.txt-3.7"></a>

## SIGNAL

Sent from the client to the server. The syntax is:
```text
    "SIGNAL" SP Signal CRLF
    
     Signal = "RELOAD" / "SHUTDOWN" / "DUMP" / "DEBUG" / "HALT" /
              "HUP" / "INT" / "USR1" / "USR2" / "TERM" / "NEWNYM" /
              "CLEARDNSCACHE" / "HEARTBEAT" / "ACTIVE" / "DORMANT"
```
The meaning of the signals are:

```text
      RELOAD    -- Reload: reload config items.
      SHUTDOWN  -- Controlled shutdown: if server is an OP, exit immediately.
                   If it's an OR, close listeners and exit after
                   ShutdownWaitLength seconds.
      DUMP      -- Dump stats: log information about open connections and
                   circuits.
      DEBUG     -- Debug: switch all open logs to loglevel debug.
      HALT      -- Immediate shutdown: clean up and exit now.
      CLEARDNSCACHE -- Forget the client-side cached IPs for all hostnames.
      NEWNYM    -- Switch to clean circuits, so new application requests
                   don't share any circuits with old ones.  Also clears
                   the client-side DNS cache.  (Tor MAY rate-limit its
                   response to this signal.)
      HEARTBEAT -- Make Tor dump an unscheduled Heartbeat message to log.
      DORMANT   -- Tell Tor to become "dormant".  A dormant Tor will
                   try to avoid CPU and network usage until it receives
                   user-initiated network request.  (Don't use this
                   on relays or hidden services yet!)
      ACTIVE    -- Tell Tor to stop being "dormant", as if it had received
                   a user-initiated network request.
```

The server responds with `250 OK` if the signal is recognized (or simply
closes the socket if it was asked to close immediately), or `552
Unrecognized signal` if the signal is unrecognized.

Note that not all of these signals have POSIX signal equivalents.  The
ones that do are as below.  You may also use these POSIX names for the
signal that have them.

```text
      RELOAD: HUP
      SHUTDOWN: INT
      HALT: TERM
      DUMP: USR1
      DEBUG: USR2
```

\[SIGNAL DORMANT and SIGNAL ACTIVE were added in 0.4.0.1-alpha.\]

<a id="control-spec.txt-3.8"></a>

## MAPADDRESS

Sent from the client to the server.  The syntax is:

```text
    "MAPADDRESS" SP 1*(Address "=" Address SP) CRLF
```

The first address in each pair is an "original" address; the second is a
"replacement" address.  The client sends this message to the server in
order to tell it that future SOCKS requests for connections to the original
address should be replaced with connections to the specified replacement
address.  If the addresses are well-formed, and the server is able to
fulfill the request, the server replies with a 250 message:

```text
    250-OldAddress1=NewAddress1
    250 OldAddress2=NewAddress2
```

containing the source and destination addresses.  If request is
malformed, the server replies with `512 syntax error in command
argument`.  If the server can't fulfill the request, it replies with
`451 resource exhausted`.

The client may decline to provide a body for the original address, and
instead send a special null address ("0.0.0.0" for IPv4, "::0" for IPv6, or
"." for hostname), signifying that the server should choose the original
address itself, and return that address in the reply.  The server
should ensure that it returns an element of address space that is unlikely
to be in actual use.  If there is already an address mapped to the
destination address, the server may reuse that mapping.

If the original address is already mapped to a different address, the old
mapping is removed.  If the original address and the destination address
are the same, the server removes any mapping in place for the original
address.

Example:

```text
    C: MAPADDRESS 1.2.3.4=torproject.org
    S: 250 1.2.3.4=torproject.org

    C: GETINFO address-mappings/control
    S: 250-address-mappings/control=1.2.3.4 torproject.org NEVER
    S: 250 OK

    C: MAPADDRESS 1.2.3.4=1.2.3.4
    S: 250 1.2.3.4=1.2.3.4

    C: GETINFO address-mappings/control
    S: 250-address-mappings/control=
    S: 250 OK
```

### Note
This feature is designed to be used to help Tor-ify applications
that need to use SOCKS4 or hostname-less SOCKS5.  There are three
approaches to doing this:

1. Somehow make them use SOCKS4a or SOCKS5-with-hostnames instead.
2. Use tor-resolve (or another interface to Tor's resolve-over-SOCKS
   feature) to resolve the hostname remotely.
   This doesn't work
   with special addresses like x.onion or x.y.exit.
3. Use MAPADDRESS to map an IP address to the desired hostname, and then
   arrange to fool the application into thinking that the hostname
   has resolved to that IP.

This functionality is designed to help implement the 3rd approach.

Mappings set by the controller last until the Tor process exits:
they never expire. If the controller wants the mapping to last only
a certain time, then it must explicitly un-map the address when that
time has elapsed.

MapAddress replies MAY contain mixed status codes.

Example:

```text
    C: MAPADDRESS xxx=@@@ 0.0.0.0=bogus1.google.com
    S: 512-syntax error: invalid address '@@@'
    S: 250 127.199.80.246=bogus1.google.com
```

<a id="control-spec.txt-3.9"></a>

## GETINFO

Sent from the client to the server.  The syntax is as for GETCONF:

```text
    "GETINFO" 1*(SP keyword) CRLF
```

Unlike GETCONF, this message is used for data that are not stored in the Tor
configuration file, and that may be longer than a single line.  On success,
one ReplyLine is sent for each requested value, followed by a final 250 OK
ReplyLine.  If a value fits on a single line, the format is:

```text
      250-keyword=value
```

If a value must be split over multiple lines, the format is:

```text
      250+keyword=
      value
      .
```
The server sends a 551 or 552 error on failure.

Recognized keys and their values include:
```text
    "version" -- The version of the server's software, which MAY include the
      name of the software, such as "Tor 0.0.9.4".  The name of the software,
      if absent, is assumed to be "Tor".

    "config-file" -- The location of Tor's configuration file ("torrc").

    "config-defaults-file" -- The location of Tor's configuration
      defaults file ("torrc.defaults").  This file gets parsed before
      torrc, and is typically used to replace Tor's default
      configuration values. [First implemented in 0.2.3.9-alpha.]

    "config-text" -- The contents that Tor would write if you send it
      a SAVECONF command, so the controller can write the file to
      disk itself. [First implemented in 0.2.2.7-alpha.]

    "exit-policy/default" -- The default exit policy lines that Tor will
      *append* to the ExitPolicy config option.

    "exit-policy/reject-private/default" -- The default exit policy lines
      that Tor will *prepend* to the ExitPolicy config option when
      ExitPolicyRejectPrivate is 1.

    "exit-policy/reject-private/relay" -- The relay-specific exit policy
      lines that Tor will *prepend* to the ExitPolicy config option based
      on the current values of ExitPolicyRejectPrivate and
      ExitPolicyRejectLocalInterfaces. These lines are based on the public
      addresses configured in the torrc and present on the relay's
      interfaces. Will send 552 error if the server is not running as
      onion router. Will send 551 on internal error which may be transient.

    "exit-policy/ipv4"
    "exit-policy/ipv6"
    "exit-policy/full" -- This OR's exit policy, in IPv4-only, IPv6-only, or
      all-entries flavors. Handles errors in the same way as "exit-policy/
      reject-private/relay" does.

    "desc/id/<OR identity>" or "desc/name/<OR nickname>" -- the latest
      server descriptor for a given OR.  (Note that modern Tor clients
      do not download server descriptors by default, but download
      microdescriptors instead.  If microdescriptors are enabled, you'll
      need to use "md" instead.)

    "md/all" -- all known microdescriptors for the entire Tor network.
      Each microdescriptor is terminated by a newline.
      [First implemented in 0.3.5.1-alpha]

    "md/id/<OR identity>" or "md/name/<OR nickname>" -- the latest
      microdescriptor for a given OR. Empty if we have no microdescriptor for
      that OR (because we haven't downloaded one, or it isn't in the
      consensus). [First implemented in 0.2.3.8-alpha.]

    "desc/download-enabled" -- "1" if we try to download router descriptors;
      "0" otherwise. [First implemented in 0.3.2.1-alpha]

    "md/download-enabled" -- "1" if we try to download microdescriptors;
      "0" otherwise. [First implemented in 0.3.2.1-alpha]

    "dormant" -- A nonnegative integer: zero if Tor is currently active and
      building circuits, and nonzero if Tor has gone idle due to lack of use
      or some similar reason.  [First implemented in 0.2.3.16-alpha]

    "desc-annotations/id/<OR identity>" -- outputs the annotations string
      (source, timestamp of arrival, purpose, etc) for the corresponding
      descriptor. [First implemented in 0.2.0.13-alpha.]

    "extra-info/digest/<digest>"  -- the extrainfo document whose digest (in
      hex) is <digest>.  Only available if we're downloading extra-info
      documents.

    "ns/id/<OR identity>" or "ns/name/<OR nickname>" -- the latest router
      status info (v3 directory style) for a given OR.  Router status
      info is as given in dir-spec.txt, and reflects the latest
      consensus opinion about the
      router in question. Like directory clients, controllers MUST
      tolerate unrecognized flags and lines.  The published date and
      descriptor digest are those believed to be best by this Tor,
      not necessarily those for a descriptor that Tor currently has.
      [First implemented in 0.1.2.3-alpha.]
      [In 0.2.0.9-alpha this switched from v2 directory style to v3]

    "ns/all" -- Router status info (v3 directory style) for all ORs we
      that the consensus has an opinion about, joined by newlines.
      [First implemented in 0.1.2.3-alpha.]
      [In 0.2.0.9-alpha this switched from v2 directory style to v3]

    "ns/purpose/<purpose>" -- Router status info (v3 directory style)
      for all ORs of this purpose. Mostly designed for /ns/purpose/bridge
      queries.
      [First implemented in 0.2.0.13-alpha.]
      [In 0.2.0.9-alpha this switched from v2 directory style to v3]
      [In versions before 0.4.1.1-alpha we set the Running flag on
       bridges when /ns/purpose/bridge is accessed]
      [In 0.4.1.1-alpha we set the Running flag on bridges when the
       bridge networkstatus file is written to disk]

    "desc/all-recent" -- the latest server descriptor for every router that
      Tor knows about.  (See md note about "desc/id" and "desc/name" above.)

    "network-status" -- [Deprecated in 0.3.1.1-alpha, removed
      in 0.4.5.1-alpha.]

    "address-mappings/all"
    "address-mappings/config"
    "address-mappings/cache"
    "address-mappings/control" -- a \r\n-separated list of address
      mappings, each in the form of "from-address to-address expiry".
      The 'config' key returns those address mappings set in the
      configuration; the 'cache' key returns the mappings in the
      client-side DNS cache; the 'control' key returns the mappings set
      via the control interface; the 'all' target returns the mappings
      set through any mechanism.
      Expiry is formatted as with ADDRMAP events, except that "expiry" is
      always a time in UTC or the string "NEVER"; see section 4.1.7.
      First introduced in 0.2.0.3-alpha.

    "addr-mappings/*" -- as for address-mappings/*, but without the
      expiry portion of the value.  Use of this value is deprecated
      since 0.2.0.3-alpha; use address-mappings instead.

    "address" -- the best guess at our external IP address. If we
      have no guess, return a 551 error. (Added in 0.1.2.2-alpha)

    "address/v4"
    "address/v6"
      the best guess at our respective external IPv4 or IPv6 address.
      If we have no guess, return a 551 error. (Added in 0.4.5.1-alpha)

    "fingerprint" -- the contents of the fingerprint file that Tor
      writes as a relay, or a 551 if we're not a relay currently.
      (Added in 0.1.2.3-alpha)

    "circuit-status"
      A series of lines as for a circuit status event. Each line is of
      the form described in section 4.1.1, omitting the initial
      "650 CIRC ".  Note that clients must be ready to accept additional
      arguments as described in section 4.1.

    "stream-status"
      A series of lines as for a stream status event.  Each is of the form:
         StreamID SP StreamStatus SP CircuitID SP Target CRLF

    "orconn-status"
      A series of lines as for an OR connection status event.  In Tor
      0.1.2.2-alpha with feature VERBOSE_NAMES enabled and in Tor
      0.2.2.1-alpha and later by default, each line is of the form:
         LongName SP ORStatus CRLF

     In Tor versions 0.1.2.2-alpha through 0.2.2.1-alpha with feature
     VERBOSE_NAMES turned off and before version 0.1.2.2-alpha, each line
     is of the form:
         ServerID SP ORStatus CRLF

    "entry-guards"
      A series of lines listing the currently chosen entry guards, if any.
      In Tor 0.1.2.2-alpha with feature VERBOSE_NAMES enabled and in Tor
      0.2.2.1-alpha and later by default, each line is of the form:
         LongName SP Status [SP ISOTime] CRLF

     In Tor versions 0.1.2.2-alpha through 0.2.2.1-alpha with feature
     VERBOSE_NAMES turned off and before version 0.1.2.2-alpha, each line
     is of the form:
         ServerID2 SP Status [SP ISOTime] CRLF
         ServerID2 = Nickname / 40*HEXDIG

      The definition of Status is the same for both:
         Status = "up" / "never-connected" / "down" /
                  "unusable" / "unlisted"

      [From 0.1.1.4-alpha to 0.1.1.10-alpha, entry-guards was called
       "helper-nodes". Tor still supports calling "helper-nodes", but it
        is deprecated and should not be used.]

      [Older versions of Tor (before 0.1.2.x-final) generated 'down' instead
       of unlisted/unusable. Between 0.1.2.x-final and 0.2.6.3-alpha,
       'down' was never generated.]

      [XXXX ServerID2 differs from ServerID in not prefixing fingerprints
       with a $.  This is an implementation error.  It would be nice to add
       the $ back in if we can do so without breaking compatibility.]

    "traffic/read" -- Total bytes read (downloaded).

    "traffic/written" -- Total bytes written (uploaded).

    "uptime" -- Uptime of the Tor daemon (in seconds).  Added in
       0.3.5.1-alpha.

    "accounting/enabled"
    "accounting/hibernating"
    "accounting/bytes"
    "accounting/bytes-left"
    "accounting/interval-start"
    "accounting/interval-wake"
    "accounting/interval-end"
      Information about accounting status.  If accounting is enabled,
      "enabled" is 1; otherwise it is 0.  The "hibernating" field is "hard"
      if we are accepting no data; "soft" if we're accepting no new
      connections, and "awake" if we're not hibernating at all.  The "bytes"
      and "bytes-left" fields contain (read-bytes SP write-bytes), for the
      start and the rest of the interval respectively.  The 'interval-start'
      and 'interval-end' fields are the borders of the current interval; the
      'interval-wake' field is the time within the current interval (if any)
      where we plan[ned] to start being active. The times are UTC.

    "config/names"
      A series of lines listing the available configuration options. Each is
      of the form:
         OptionName SP OptionType [ SP Documentation ] CRLF
         OptionName = Keyword
         OptionType = "Integer" / "TimeInterval" / "TimeMsecInterval" /
           "DataSize" / "Float" / "Boolean" / "Time" / "CommaList" /
           "Dependent" / "Virtual" / "String" / "LineList"
         Documentation = Text
      Note: The incorrect spelling "Dependant" was used from the time this key
      was introduced in Tor 0.1.1.4-alpha until it was corrected in Tor
      0.3.0.2-alpha.  It is recommended that clients accept both spellings.

    "config/defaults"
      A series of lines listing default values for each configuration
      option. Options which don't have a valid default don't show up
      in the list.  Introduced in Tor 0.2.4.1-alpha.
         OptionName SP OptionValue CRLF
         OptionName = Keyword
         OptionValue = Text

    "info/names"
      A series of lines listing the available GETINFO options.  Each is of
      one of these forms:
         OptionName SP Documentation CRLF
         OptionPrefix SP Documentation CRLF
         OptionPrefix = OptionName "/*"
      The OptionPrefix form indicates a number of options beginning with the
      prefix. So if "config/*" is listed, other options beginning with
      "config/" will work, but "config/*" itself is not an option.

    "events/names"
      A space-separated list of all the events supported by this version of
      Tor's SETEVENTS.

    "features/names"
      A space-separated list of all the features supported by this version
      of Tor's USEFEATURE.

    "signal/names"
      A space-separated list of all the values supported by the SIGNAL
      command.

    "ip-to-country/ipv4-available"
    "ip-to-country/ipv6-available"
      "1" if the relevant geoip or geoip6 database is present; "0" otherwise.
      This field was added in Tor 0.3.2.1-alpha.

    "ip-to-country/*"
      Maps IP addresses to 2-letter country codes.  For example,
      "GETINFO ip-to-country/18.0.0.1" should give "US".

    "process/pid" -- Process id belonging to the main tor process.
    "process/uid" -- User id running the tor process, -1 if unknown (this is
     unimplemented on Windows, returning -1).
    "process/user" -- Username under which the tor process is running,
     providing an empty string if none exists (this is unimplemented on
     Windows, returning an empty string).
    "process/descriptor-limit" -- Upper bound on the file descriptor limit, -1
     if unknown

    "dir/status-vote/current/consensus" [added in Tor 0.2.1.6-alpha]
    "dir/status-vote/current/consensus-microdesc" [added in Tor 0.4.3.1-alpha]
    "dir/status/authority"
    "dir/status/fp/<F>"
    "dir/status/fp/<F1>+<F2>+<F3>"
    "dir/status/all"
    "dir/server/fp/<F>"
    "dir/server/fp/<F1>+<F2>+<F3>"
    "dir/server/d/<D>"
    "dir/server/d/<D1>+<D2>+<D3>"
    "dir/server/authority"
    "dir/server/all"
      A series of lines listing directory contents, provided according to the
      specification for the URLs listed in Section 4.4 of dir-spec.txt.  Note
      that Tor MUST NOT provide private information, such as descriptors for
      routers not marked as general-purpose.  When asked for 'authority'
      information for which this Tor is not authoritative, Tor replies with
      an empty string.

      Note that, as of Tor 0.2.3.3-alpha, Tor clients don't download server
      descriptors anymore, but microdescriptors.  So, a "551 Servers
      unavailable" reply to all "GETINFO dir/server/*" requests is actually
      correct.  If you have an old program which absolutely requires server
      descriptors to work, try setting UseMicrodescriptors 0 or
      FetchUselessDescriptors 1 in your client's torrc.

    "status/circuit-established"
    "status/enough-dir-info"
    "status/good-server-descriptor"
    "status/accepted-server-descriptor"
    "status/..."
      These provide the current internal Tor values for various Tor
      states. See Section 4.1.10 for explanations. (Only a few of the
      status events are available as getinfo's currently. Let us know if
      you want more exposed.)
    "status/reachability-succeeded/or"
      0 or 1, depending on whether we've found our ORPort reachable.
    "status/reachability-succeeded/dir"
      0 or 1, depending on whether we've found our DirPort reachable.
      1 if there is no DirPort, and therefore no need for a reachability
      check.
    "status/reachability-succeeded"
      "OR=" ("0"/"1") SP "DIR=" ("0"/"1")
      Combines status/reachability-succeeded/*; controllers MUST ignore
      unrecognized elements in this entry.
    "status/bootstrap-phase"
      Returns the most recent bootstrap phase status event
      sent. Specifically, it returns a string starting with either
      "NOTICE BOOTSTRAP ..." or "WARN BOOTSTRAP ...". Controllers should
      use this getinfo when they connect or attach to Tor to learn its
      current bootstrap state.
    "status/version/recommended"
      List of currently recommended versions.
    "status/version/current"
      Status of the current version. One of: new, old, unrecommended,
      recommended, new in series, obsolete, unknown.
    "status/clients-seen"
      A summary of which countries we've seen clients from recently,
      formatted the same as the CLIENTS_SEEN status event described in
      Section 4.1.14. This GETINFO option is currently available only
      for bridge relays.
    "status/fresh-relay-descs"
      Provides fresh server and extra-info descriptors for our relay. Note
      this is *not* the latest descriptors we've published, but rather what we
      would generate if we needed to make a new descriptor right now.

    "net/listeners/*"

      A quoted, space-separated list of the locations where Tor is listening
      for connections of the specified type. These can contain IPv4
      network address...

        "127.0.0.1:9050" "127.0.0.1:9051"

      ... or local unix sockets...

        "unix:/home/my_user/.tor/socket"

      ... or IPv6 network addresses:

        "[2001:0db8:7000:0000:0000:dead:beef:1234]:9050"

      [New in Tor 0.2.2.26-beta.]

    "net/listeners/or"

      Listeners for OR connections. Talks Tor protocol as described in
      tor-spec.txt.

    "net/listeners/dir"

      Listeners for Tor directory protocol, as described in dir-spec.txt.

    "net/listeners/socks"

      Listeners for onion proxy connections that talk SOCKS4/4a/5 protocol.

    "net/listeners/trans"

      Listeners for transparent connections redirected by firewall, such as
      pf or netfilter.

    "net/listeners/natd"

      Listeners for transparent connections redirected by natd.

    "net/listeners/dns"

      Listeners for a subset of DNS protocol that Tor network supports.

    "net/listeners/control"

      Listeners for Tor control protocol, described herein.

    "net/listeners/extor"

      Listeners corresponding to Extended ORPorts for integration with
      pluggable transports. See proposals 180 and 196.

    "net/listeners/httptunnel"

      Listeners for onion proxy connections that leverage HTTP CONNECT
      tunnelling.

      [The extor and httptunnel lists were added in 0.3.2.12, 0.3.3.10, and
      0.3.4.6-rc.]

    "dir-usage"
      A newline-separated list of how many bytes we've served to answer
      each type of directory request. The format of each line is:
         Keyword 1*SP Integer 1*SP Integer
      where the first integer is the number of bytes written, and the second
      is the number of requests answered.

      [This feature was added in Tor 0.2.2.1-alpha, and removed in
       Tor 0.2.9.1-alpha. Even when it existed, it only provided
       useful output when the Tor client was built with either the
       INSTRUMENT_DOWNLOADS or RUNNING_DOXYGEN compile-time options.]

    "bw-event-cache"
      A space-separated summary of recent BW events in chronological order
      from oldest to newest.  Each event is represented by a comma-separated
      tuple of "R,W", R is the number of bytes read, and W is the number of
      bytes written.  These entries each represent about one second's worth
      of traffic.
      [New in Tor 0.2.6.3-alpha]

     "consensus/valid-after"
     "consensus/fresh-until"
     "consensus/valid-until"
      Each of these produces an ISOTime describing part of the lifetime of
      the current (valid, accepted) consensus that Tor has.
      [New in Tor 0.2.6.3-alpha]

    "hs/client/desc/id/<ADDR>"
      Prints the content of the hidden service descriptor corresponding to
      the given <ADDR> which is an onion address without the ".onion" part.
      The client's cache is queried to find the descriptor. The format of
      the descriptor is described in section 1.3 of the rend-spec.txt
      document.

      If <ADDR> is unrecognized or if not found in the cache, a 551 error is
      returned.

      [New in Tor 0.2.7.1-alpha]
      [HS v3 support added 0.3.3.1-alpha]

    "hs/service/desc/id/<ADDR>"
      Prints the content of the hidden service descriptor corresponding to
      the given <ADDR> which is an onion address without the ".onion" part.
      The service's local descriptor cache is queried to find the descriptor.
      The format of the descriptor is described in section 1.3 of the
      rend-spec.txt document.

      If <ADDR> is unrecognized or if not found in the cache, a 551 error is
      returned.

      [New in Tor 0.2.7.2-alpha]
      [HS v3 support added 0.3.3.1-alpha]

    "onions/current"
    "onions/detached"
      A newline-separated list of the Onion ("Hidden") Services created
      via the "ADD_ONION" command. The 'current' key returns Onion Services
      belonging to the current control connection. The 'detached' key
      returns Onion Services detached from the parent control connection
      (as in, belonging to no control connection).
      The format of each line is:
         HSAddress
      [New in Tor 0.2.7.1-alpha.]
      [HS v3 support added 0.3.3.1-alpha]

    "network-liveness"
      The string "up" or "down", indicating whether we currently believe the
      network is reachable.

    "downloads/"
      The keys under downloads/ are used to query download statuses; they all
      return either a sequence of newline-terminated hex encoded digests, or
      a "serialized download status" as follows:

       SerializedDownloadStatus =
         -- when do we plan to next attempt to download this object?
         "next-attempt-at" SP ISOTime CRLF
         -- how many times have we failed since the last success?
         "n-download-failures" SP UInt CRLF
         -- how many times have we tried to download this?
         "n-download-attempts" SP UInt CRLF
         -- according to which schedule rule will we download this?
         "schedule" SP DownloadSchedule CRLF
         -- do we want to fetch this from an authority, or will any cache do?
         "want-authority" SP DownloadWantAuthority CRLF
         -- do we increase our download delay whenever we fail to fetch this,
         -- or whenever we attempt fetching this?
         "increment-on" SP DownloadIncrementOn CRLF
         -- do we increase the download schedule deterministically, or at
         -- random?
         "backoff" SP DownloadBackoff CRLF
         [
           -- with an exponential backoff, where are we in the schedule?
           "last-backoff-position" Uint CRLF
           -- with an exponential backoff, what was our last delay?
           "last-delay-used UInt CRLF
         ]

      where

      DownloadSchedule =
        "DL_SCHED_GENERIC" / "DL_SCHED_CONSENSUS" / "DL_SCHED_BRIDGE"
      DownloadWantAuthority =
        "DL_WANT_ANY_DIRSERVER" / "DL_WANT_AUTHORITY"
      DownloadIncrementOn =
        "DL_SCHED_INCREMENT_FAILURE" / "DL_SCHED_INCREMENT_ATTEMPT"
      DownloadBackoff =
        "DL_SCHED_DETERMINISTIC" / "DL_SCHED_RANDOM_EXPONENTIAL"

      The optional last two lines must be present if DownloadBackoff is
      "DL_SCHED_RANDOM_EXPONENTIAL" and must be absent if DownloadBackoff
      is "DL_SCHED_DETERMINISTIC".

      In detail, the keys supported are:

      "downloads/networkstatus/ns"
        The SerializedDownloadStatus for the NS-flavored consensus for
        whichever bootstrap state Tor is currently in.

      "downloads/networkstatus/ns/bootstrap"
        The SerializedDownloadStatus for the NS-flavored consensus at
        bootstrap time, regardless of whether we are currently bootstrapping.

      "downloads/networkstatus/ns/running"

        The SerializedDownloadStatus for the NS-flavored consensus when
        running, regardless of whether we are currently bootstrapping.

      "downloads/networkstatus/microdesc"
        The SerializedDownloadStatus for the microdesc-flavored consensus for
        whichever bootstrap state Tor is currently in.

      "downloads/networkstatus/microdesc/bootstrap"
        The SerializedDownloadStatus for the microdesc-flavored consensus at
        bootstrap time, regardless of whether we are currently bootstrapping.

      "downloads/networkstatus/microdesc/running"
        The SerializedDownloadStatus for the microdesc-flavored consensus when
        running, regardless of whether we are currently bootstrapping.

      "downloads/cert/fps"

        A newline-separated list of hex-encoded digests for authority
        certificates for which we have download status available.

      "downloads/cert/fp/<Fingerprint>"
        A SerializedDownloadStatus for the default certificate for the
        identity digest <Fingerprint> returned by the downloads/cert/fps key.

      "downloads/cert/fp/<Fingerprint>/sks"
        A newline-separated list of hex-encoded signing key digests for the
        authority identity digest <Fingerprint> returned by the
        downloads/cert/fps key.

      "downloads/cert/fp/<Fingerprint>/<SKDigest>"
        A SerializedDownloadStatus for the certificate for the identity
        digest <Fingerprint> returned by the downloads/cert/fps key and signing
        key digest <SKDigest> returned by the downloads/cert/fp/<Fingerprint>/
        sks key.

      "downloads/desc/descs"
        A newline-separated list of hex-encoded router descriptor digests
        [note, not identity digests - the Tor process may not have seen them
        yet while downloading router descriptors].  If the Tor process is not
        using a NS-flavored consensus, a 551 error is returned.

      "downloads/desc/<Digest>"
        A SerializedDownloadStatus for the router descriptor with digest
        <Digest> as returned by the downloads/desc/descs key.  If the Tor
        process is not using a NS-flavored consensus, a 551 error is returned.

      "downloads/bridge/bridges"
        A newline-separated list of hex-encoded bridge identity digests.  If
        the Tor process is not using bridges, a 551 error is returned.

      "downloads/bridge/<Digest>"
        A SerializedDownloadStatus for the bridge descriptor with identity
        digest <Digest> as returned by the downloads/bridge/bridges key.  If
        the Tor process is not using bridges, a 551 error is returned.

    "sr/current"
    "sr/previous"
      The current or previous shared random value, as received in the
      consensus, base-64 encoded.  An empty value means that either
      the consensus has no shared random value, or Tor has no consensus.

    "current-time/local"
    "current-time/utc"
      The current system or UTC time, as returned by the system, in ISOTime2
      format.  (Introduced in 0.3.4.1-alpha.)

    "stats/ntor/requested"
    "stats/ntor/assigned"
      The NTor circuit onion handshake rephist values which are requested or
      assigned.  (Introduced in 0.4.5.1-alpha)

    "stats/tap/requested"
    "stats/tap/assigned"
      The TAP circuit onion handshake rephist values which are requested or
      assigned.  (Introduced in 0.4.5.1-alpha)

    "config-can-saveconf"
      0 or 1, depending on whether it is possible to use SAVECONF without the
      FORCE flag. (Introduced in 0.3.1.1-alpha.)

    "limits/max-mem-in-queues"
      The amount of memory that Tor's out-of-memory checker will allow
      Tor to allocate (in places it can see) before it starts freeing memory
      and killing circuits. See the MaxMemInQueues option for more
      details. Unlike the option, this value reflects Tor's actual limit, and
      may be adjusted depending on the available system memory rather than on
      the MaxMemInQueues option. (Introduced in 0.2.5.4-alpha)
```

Example:
```text
     C: GETINFO version desc/name/moria1
     S: 250+desc/name/moria=
     S: [Descriptor for moria]
     S: .
     S: 250-version=Tor 0.1.1.0-alpha-cvs
     S: 250 OK
```

<a id="control-spec.txt-3.10"></a>

## EXTENDCIRCUIT

Sent from the client to the server.  The format is:

```text
      "EXTENDCIRCUIT" SP CircuitID
                      [SP ServerSpec *("," ServerSpec)]
                      [SP "purpose=" Purpose] CRLF
```

This request takes one of two forms: either the CircuitID is zero, in
which case it is a request for the server to build a new circuit,
or the CircuitID is nonzero, in which case it is a request for the
server to extend an existing circuit with that ID according to the
specified path.

If the CircuitID is 0, the controller has the option of providing
a path for Tor to use to build the circuit. If it does not provide
a path, Tor will select one automatically from high capacity nodes
according to path-spec.txt.

If CircuitID is 0 and "purpose=" is specified, then the circuit's
purpose is set. Two choices are recognized: "general" and
"controller". If not specified, circuits are created as "general".

If the request is successful, the server sends a reply containing a
message body consisting of the CircuitID of the (maybe newly created)
circuit. The syntax is:
```text
    "250" SP "EXTENDED" SP CircuitID CRLF
```

<a id="control-spec.txt-3.11"></a>

## SETCIRCUITPURPOSE

Sent from the client to the server.  The format is:

```text
    "SETCIRCUITPURPOSE" SP CircuitID SP "purpose=" Purpose CRLF
```

This changes the circuit's purpose. See EXTENDCIRCUIT above for details.

<a id="control-spec.txt-3.12"></a>

## SETROUTERPURPOSE

Sent from the client to the server.  The format is:

```text
    "SETROUTERPURPOSE" SP NicknameOrKey SP Purpose CRLF
```
This changes the descriptor's purpose. See +POSTDESCRIPTOR below
for details.

NOTE: This command was disabled and made obsolete as of Tor
0.2.0.8-alpha. It doesn't exist anymore, and is listed here only for
historical interest.

<a id="control-spec.txt-3.13"></a>

## ATTACHSTREAM

Sent from the client to the server.  The syntax is:

```text
    "ATTACHSTREAM" SP StreamID SP CircuitID [SP "HOP=" HopNum] CRLF
```
This message informs the server that the specified stream should be
associated with the specified circuit.  Each stream may be associated with
at most one circuit, and multiple streams may share the same circuit.
Streams can only be attached to completed circuits (that is, circuits that
have sent a circuit status 'BUILT' event or are listed as built in a
GETINFO circuit-status request).

If the circuit ID is 0, responsibility for attaching the given stream is
returned to Tor.

If HOP=HopNum is specified, Tor will choose the HopNumth hop in the
circuit as the exit node, rather than the last node in the circuit.
Hops are 1-indexed; generally, it is not permitted to attach to hop 1.

Tor responds with `250 OK` if it can attach the stream, `552` if the
circuit or stream didn't exist, `555` if the stream isn't in an
appropriate state to be attached (e.g. it's already open), or `551` if
the stream couldn't be attached for another reason.

{Implementation note: Tor will close unattached streams by itself,
roughly two minutes after they are born. Let the developers know if
that turns out to be a problem.}

{Implementation note: By default, Tor automatically attaches streams to
circuits itself, unless the configuration variable
"\_\_LeaveStreamsUnattached" is set to "1".  Attempting to attach streams
via TC when "\_\_LeaveStreamsUnattached" is false may cause a race between
Tor and the controller, as both attempt to attach streams to circuits.}

{Implementation note: You can try to attachstream to a stream that
has already sent a connect or resolve request but hasn't succeeded
yet, in which case Tor will detach the stream from its current circuit
before proceeding with the new attach request.}

<a id="control-spec.txt-3.14"></a>

## POSTDESCRIPTOR

Sent from the client to the server. The syntax is:

```text
    "+POSTDESCRIPTOR" [SP "purpose=" Purpose] [SP "cache=" Cache]
                      CRLF Descriptor CRLF "." CRLF
```

This message informs the server about a new descriptor. If Purpose is
specified, it must be either "general", "controller", or "bridge",
else we return a `552` error. The default is "general".

If Cache is specified, it must be either "no" or "yes", else we
return a `552` error. If Cache is not specified, Tor will decide for
itself whether it wants to cache the descriptor, and controllers
must not rely on its choice.

The descriptor, when parsed, must contain a number of well-specified
fields, including fields for its nickname and identity.

If there is an error in parsing the descriptor, the server must send a
`554 Invalid descriptor` reply. If the descriptor is well-formed but
the server chooses not to add it, it must reply with a `251` message
whose body explains why the server was not added. If the descriptor
is added, Tor replies with `250 OK`.

<a id="control-spec.txt-3.15"></a>

## REDIRECTSTREAM

Sent from the client to the server. The syntax is:

```text
    "REDIRECTSTREAM" SP StreamID SP Address [SP Port] CRLF
```

Tells the server to change the exit address on the specified stream.  If
Port is specified, changes the destination port as well.  No remapping
is performed on the new provided address.

To be sure that the modified address will be used, this event must be sent
after a new stream event is received, and before attaching this stream to
a circuit.

Tor replies with `250 OK` on success.

<a id="control-spec.txt-3.16"></a>

## CLOSESTREAM

Sent from the client to the server.  The syntax is:

```text
    "CLOSESTREAM" SP StreamID SP Reason *(SP Flag) CRLF
```

Tells the server to close the specified stream.  The reason should be one
of the Tor RELAY_END reasons given in tor-spec.txt, as a decimal.  Flags is
not used currently; Tor servers SHOULD ignore unrecognized flags.  Tor may
hold the stream open for a while to flush any data that is pending.

Tor replies with `250 OK` on success, or a `512` if there aren't enough
arguments, or a `552` if it doesn't recognize the StreamID or reason.

<a id="control-spec.txt-3.17"></a>

## CLOSECIRCUIT

The syntax is:

```text
     "CLOSECIRCUIT" SP CircuitID *(SP Flag) CRLF
     Flag = "IfUnused"
```

Tells the server to close the specified circuit. If "IfUnused" is
provided, do not close the circuit unless it is unused.

Other flags may be defined in the future; Tor SHOULD ignore unrecognized
flags.

Tor replies with `250 OK` on success, or a `512` if there aren't enough
arguments, or a `552` if it doesn't recognize the CircuitID.

<a id="control-spec.txt-3.18"></a>

## QUIT

Tells the server to hang up on this controller connection. This command
can be used before authenticating.

<a id="control-spec.txt-3.19"></a>

## USEFEATURE

Adding additional features to the control protocol sometimes will break
backwards compatibility. Initially such features are added into Tor and
disabled by default. USEFEATURE can enable these additional features.

The syntax is:

```text
    "USEFEATURE" *(SP FeatureName) CRLF
    FeatureName = 1*(ALPHA / DIGIT / "_" / "-")
```
Feature names are case-insensitive.

Once enabled, a feature stays enabled for the duration of the connection
to the controller. A new connection to the controller must be opened to
disable an enabled feature.

Features are a forward-compatibility mechanism; each feature will eventually
become a standard part of the control protocol. Once a feature becomes part
of the protocol, it is always-on. Each feature documents the version it was
introduced as a feature and the version in which it became part of the
protocol.

Tor will ignore a request to use any feature that is always-on. Tor will give
a `552` error in response to an unrecognized feature.

### EXTENDED_EVENTS

Same as passing 'EXTENDED' to SETEVENTS;
this is the preferred way to request the extended event syntax.

This feature was first introduced in 0.1.2.3-alpha.
It is always-on and part of the protocol in Tor 0.2.2.1-alpha and later.

### VERBOSE_NAMES

Replaces ServerID with LongName in events and GETINFO results. LongName
provides a Fingerprint for all routers, an indication of Named status,
and a Nickname if one is known. LongName is strictly more informative
than ServerID, which only provides either a Fingerprint or a Nickname.

This feature was first introduced in 0.1.2.2-alpha. It is always-on and
part of the protocol in Tor 0.2.2.1-alpha and later.

<a id="control-spec.txt-3.20"></a>

## RESOLVE

The syntax is

```text
    "RESOLVE" *Option *Address CRLF
    Option = "mode=reverse"
    Address = a hostname or IPv4 address
```

This command launches a remote hostname lookup request for every specified
request (or reverse lookup if "mode=reverse" is specified).  Note that the
request is done in the background: to see the answers, your controller will
need to listen for ADDRMAP events; see 4.1.7 below.

\[Added in Tor 0.2.0.3-alpha\]

<a id="control-spec.txt-3.21"></a>

## PROTOCOLINFO

The syntax is:

```text
    "PROTOCOLINFO" *(SP PIVERSION) CRLF
```
The server reply format is:
```text
    "250-PROTOCOLINFO" SP PIVERSION CRLF \*InfoLine "250 OK" CRLF

    InfoLine = AuthLine / VersionLine / OtherLine

    AuthLine = "250-AUTH" SP "METHODS=" AuthMethod *("," AuthMethod)
                       *(SP "COOKIEFILE=" AuthCookieFile) CRLF
    VersionLine = "250-VERSION" SP "Tor=" TorVersion OptArguments CRLF

    AuthMethod =
      "NULL"           / ; No authentication is required
      "HASHEDPASSWORD" / ; A controller must supply the original password
      "COOKIE"         / ; ... or supply the contents of a cookie file
      "SAFECOOKIE"       ; ... or prove knowledge of a cookie file's contents

    AuthCookieFile = QuotedString
    TorVersion = QuotedString

    OtherLine = "250-" Keyword OptArguments CRLF

    PIVERSION: 1*DIGIT
```

This command tells the controller what kinds of authentication are
supported.

Tor MAY give its InfoLines in any order; controllers MUST ignore InfoLines
with keywords they do not recognize.  Controllers MUST ignore extraneous
data on any InfoLine.

PIVERSION is there in case we drastically change the syntax one day. For
now it should always be "1".  Controllers MAY provide a list of the
protocolinfo versions they support; Tor MAY select a version that the
controller does not support.

AuthMethod is used to specify one or more control authentication
methods that Tor currently accepts.

AuthCookieFile specifies the absolute path and filename of the
authentication cookie that Tor is expecting and is provided iff the
METHODS field contains the method "COOKIE" and/or "SAFECOOKIE".
Controllers MUST handle escape sequences inside this string.

All authentication cookies are 32 bytes long.  Controllers MUST NOT
use the contents of a non-32-byte-long file as an authentication
cookie.

If the METHODS field contains the method "SAFECOOKIE", every
AuthCookieFile must contain the same authentication cookie.

The COOKIE authentication method exposes the user running a
controller to an unintended information disclosure attack whenever
the controller has greater filesystem read access than the process
that it has connected to.  (Note that a controller may connect to a
process other than Tor.)  It is almost never safe to use, even if
the controller's user has explicitly specified which filename to
read an authentication cookie from.  For this reason, the COOKIE
authentication method has been deprecated and will be removed from
a future version of Tor.

The VERSION line contains the Tor version.

\[Unlike other commands besides AUTHENTICATE, PROTOCOLINFO may be used (but
only once!) before AUTHENTICATE.\]

\[PROTOCOLINFO was not supported before Tor 0.2.0.5-alpha.\]

<a id="control-spec.txt-3.22"></a>

## LOADCONF

The syntax is:
```text
    "+LOADCONF" CRLF ConfigText CRLF "." CRLF
```

This command allows a controller to upload the text of a config file
to Tor over the control port.  This config file is then loaded as if
it had been read from disk.

\[LOADCONF was added in Tor 0.2.1.1-alpha.\]

<a id="control-spec.txt-3.23"></a>

## TAKEOWNERSHIP

The syntax is:
```text
    "TAKEOWNERSHIP" CRLF
```
This command instructs Tor to shut down when this control
connection is closed.  This command affects each control connection
that sends it independently; if multiple control connections send
the TAKEOWNERSHIP command to a Tor instance, Tor will shut down when
any of those connections closes.

(As of Tor 0.2.5.2-alpha, Tor does not wait a while for circuits to
close when shutting down because of an exiting controller.  If you
want to ensure a clean shutdown--and you should!--then send "SIGNAL
SHUTDOWN" and wait for the Tor process to close.)

This command is intended to be used with the
\_\_OwningControllerProcess configuration option.  A controller that
starts a Tor process which the user cannot easily control or stop
should 'own' that Tor process:

```text
    * When starting Tor, the controller should specify its PID in an
      __OwningControllerProcess on Tor's command line.  This will
      cause Tor to poll for the existence of a process with that PID,
      and exit if it does not find such a process.  (This is not a
      completely reliable way to detect whether the 'owning
      controller' is still running, but it should work well enough in
      most cases.)

    * Once the controller has connected to Tor's control port, it
      should send the TAKEOWNERSHIP command along its control
      connection.  At this point, *both* the TAKEOWNERSHIP command and
      the __OwningControllerProcess option are in effect: Tor will
      exit when the control connection ends *and* Tor will exit if it
      detects that there is no process with the PID specified in the
      __OwningControllerProcess option.

    * After the controller has sent the TAKEOWNERSHIP command, it
      should send "RESETCONF __OwningControllerProcess" along its
      control connection.  This will cause Tor to stop polling for the
      existence of a process with its owning controller's PID; Tor
      will still exit when the control connection ends.
```

\[TAKEOWNERSHIP was added in Tor 0.2.2.28-beta.\]


<a id="control-spec.txt-3.24"></a>

## AUTHCHALLENGE

The syntax is:

```text
    "AUTHCHALLENGE" SP "SAFECOOKIE"
                    SP ClientNonce
                    CRLF

    ClientNonce = 2*HEXDIG / QuotedString
```

This command is used to begin the authentication routine for the
SAFECOOKIE method of authentication.

If the server accepts the command, the server reply format is:

```text
    "250 AUTHCHALLENGE"
            SP "SERVERHASH=" ServerHash
            SP "SERVERNONCE=" ServerNonce
            CRLF

    ServerHash = 64*64HEXDIG
    ServerNonce = 64*64HEXDIG
```

The ClientNonce, ServerHash, and ServerNonce values are
encoded/decoded in the same way as the argument passed to the
AUTHENTICATE command.  ServerNonce MUST be 32 bytes long.

ServerHash is computed as:

```text
    HMAC-SHA256("Tor safe cookie authentication server-to-controller hash",
                CookieString | ClientNonce | ServerNonce)

  (with the HMAC key as its first argument)
```

After a controller sends a successful AUTHCHALLENGE command, the
next command sent on the connection must be an AUTHENTICATE command,
and the only authentication string which that AUTHENTICATE command
will accept is:

```text
    HMAC-SHA256("Tor safe cookie authentication controller-to-server hash",
                CookieString | ClientNonce | ServerNonce)
```

\[Unlike other commands besides AUTHENTICATE, AUTHCHALLENGE may be
used (but only once!) before AUTHENTICATE.\]

\[AUTHCHALLENGE was added in Tor 0.2.3.13-alpha.\]

<a id="control-spec.txt-3.25"></a>

## DROPGUARDS

The syntax is:
```text
    "DROPGUARDS" CRLF
```
Tells the server to drop all guard nodes. Do not invoke this command
lightly; it can increase vulnerability to tracking attacks over time.

Tor replies with `250 OK` on success.

\[DROPGUARDS was added in Tor 0.2.5.2-alpha.\]

<a id="control-spec.txt-3.26"></a>

## HSFETCH

The syntax is:

```text
    "HSFETCH" SP (HSAddress / "v" Version "-" DescId)
              *[SP "SERVER=" Server] CRLF

    HSAddress = 16*Base32Character / 56*Base32Character
    Version = "2" / "3"
    DescId = 32*Base32Character
    Server = LongName
```

This command launches hidden service descriptor fetch(es) for the given
HSAddress or DescId.

HSAddress can be version 2 or version 3 addresses. DescIDs can only be
version 2 IDs. Version 2 addresses consist of 16*Base32Character and
version 3 addresses consist of 56*Base32Character.

If a DescId is specified, at least one Server MUST also be provided,
otherwise a 512 error is returned. If no DescId and Server(s) are specified,
it behaves like a normal Tor client descriptor fetch. If one or more
Server are given, they are used instead triggering a fetch on each of them
in parallel.

The caching behavior when fetching a descriptor using this command is
identical to normal Tor client behavior.

Details on how to compute a descriptor id (DescId) can be found in
rend-spec.txt section 1.3.

If any values are unrecognized, a 513 error is returned and the command is
stopped. On success, Tor replies "250 OK" then Tor MUST eventually follow
this with both a HS_DESC and HS_DESC_CONTENT events with the results. If
SERVER is specified then events are emitted for each location.

Examples are:

```text
     C: HSFETCH v2-gezdgnbvgy3tqolbmjrwizlgm5ugs2tl
        SERVER=9695DFC35FFEB861329B9F1AB04C46397020CE31
     S: 250 OK

     C: HSFETCH ajkhdsfuygaesfaa
     S: 250 OK

     C: HSFETCH vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd
     S: 250 OK
```

\[HSFETCH was added in Tor 0.2.7.1-alpha\]
\[HS v3 support added 0.4.1.1-alpha\]

<a id="control-spec.txt-3.27"></a>

## ADD_ONION

The syntax is:

```text
    "ADD_ONION" SP KeyType ":" KeyBlob
            [SP "Flags=" Flag *("," Flag)]
            [SP "MaxStreams=" NumStreams]
            1*(SP "Port=" VirtPort ["," Target])
            *(SP "ClientAuth=" ClientName [":" ClientBlob]) CRLF
            *(SP "ClientAuthV3=" V3Key) CRLF

    KeyType =
     "NEW"     / ; The server should generate a key of algorithm KeyBlob
     "RSA1024" / ; The server should use the 1024 bit RSA key provided
                   in as KeyBlob (v2).
     "ED25519-V3"; The server should use the ed25519 v3 key provided in as
                   KeyBlob (v3).

    KeyBlob =
     "BEST"    / ; The server should generate a key using the "best"
                   supported algorithm (KeyType == "NEW").
                   [As of 0.4.2.3-alpha, ED25519-V3 is used]
     "RSA1024" / ; The server should generate a 1024 bit RSA key
                   (KeyType == "NEW") (v2).
     "ED25519-V3"; The server should generate an ed25519 private key
                   (KeyType == "NEW") (v3).
     String      ; A serialized private key (without whitespace)

    Flag =
     "DiscardPK" / ; The server should not include the newly generated
                     private key as part of the response.
     "Detach"    / ; Do not associate the newly created Onion Service
                     to the current control connection.
     "BasicAuth" / ; Client authorization is required using the "basic"
                     method (v2 only).
     "V3Auth"    / ; Version 3 client authorization is required (v3 only).

     "NonAnonymous" /; Add a non-anonymous Single Onion Service. Tor
                       checks this flag matches its configured hidden
                       service anonymity mode.
     "MaxStreamsCloseCircuit"; Close the circuit is the maximum streams
                               allowed is reached.

    NumStreams = A value between 0 and 65535 which is used as the maximum
                 streams that can be attached on a rendezvous circuit. Setting
                 it to 0 means unlimited which is also the default behavior.

    VirtPort = The virtual TCP Port for the Onion Service (As in the
               HiddenServicePort "VIRTPORT" argument).

    Target = The (optional) target for the given VirtPort (As in the
             optional HiddenServicePort "TARGET" argument).

    ClientName = An identifier 1 to 16 characters long, using only
                 characters in A-Za-z0-9+-_ (no spaces) (v2 only).

    ClientBlob = Authorization data for the client, in an opaque format
                 specific to the authorization method (v2 only).

    V3Key = The client's base32-encoded x25519 public key, using only the key
            part of rend-spec-v3.txt section G.1.2 (v3 only).
```

The server reply format is:

```text
    "250-ServiceID=" ServiceID CRLF
    ["250-PrivateKey=" KeyType ":" KeyBlob CRLF]
    *("250-ClientAuth=" ClientName ":" ClientBlob CRLF)
    "250 OK" CRLF

    ServiceID = The Onion Service address without the trailing ".onion"
                suffix
```

Tells the server to create a new Onion ("Hidden") Service, with the
specified private key and algorithm.  If a KeyType of "NEW" is selected,
the server will generate a new keypair using the selected algorithm.
The "Port" argument's VirtPort and Target values have identical
semantics to the corresponding HiddenServicePort configuration values.

The server response will only include a private key if the server was
requested to generate a new keypair, and also the "DiscardPK" flag was
not specified. (Note that if "DiscardPK" flag is specified, there is no
way to recreate the generated keypair and the corresponding Onion
Service at a later date).

If client authorization is enabled using the "BasicAuth" flag (which is v2
only), the service will not be accessible to clients without valid
authorization data (configured with the "HidServAuth" option).  The list of
authorized clients is specified with one or more "ClientAuth" parameters.
If "ClientBlob" is not specified for a client, a new credential will be
randomly generated and returned.

Tor instances can either be in anonymous hidden service mode, or
non-anonymous single onion service mode. All hidden services on the same
tor instance have the same anonymity. To guard against unexpected loss
of anonymity, Tor checks that the ADD_ONION "NonAnonymous" flag matches
the current hidden service anonymity mode. The hidden service anonymity
mode is configured using the Tor options HiddenServiceSingleHopMode and
HiddenServiceNonAnonymousMode. If both these options are 1, the
"NonAnonymous" flag must be provided to ADD_ONION. If both these options
are 0 (the Tor default), the flag must NOT be provided.

Once created the new Onion Service will remain active until either the
Onion Service is removed via "DEL_ONION", the server terminates, or the
control connection that originated the "ADD_ONION" command is closed.
It is possible to override disabling the Onion Service on control
connection close by specifying the "Detach" flag.

It is the Onion Service server application's responsibility to close
existing client connections if desired after the Onion Service is
removed.

(The KeyBlob format is left intentionally opaque, however for "RSA1024"
keys it is currently the Base64 encoded DER representation of a PKCS#1
RSAPrivateKey, with all newlines removed. For a "ED25519-V3" key is
the Base64 encoding of the concatenation of the 32-byte ed25519 secret
scalar in little-endian and the 32-byte ed25519 PRF secret.)

\[Note: The ED25519-V3 format is not the same as, e.g., SUPERCOP
ed25519/ref, which stores the concatenation of the 32-byte ed25519
hash seed concatenated with the 32-byte public key, and which derives
the secret scalar and PRF secret by expanding the hash seed with
SHA-512.  Our key blinding scheme is incompatible with storing
private keys as seeds, so we store the secret scalar alongside the
PRF secret, and just pay the cost of recomputing the public key when
importing an ED25519-V3 key.\]

Examples:

```text
     C: ADD_ONION NEW:BEST Flags=DiscardPK Port=80
     S: 250-ServiceID=exampleoniont2pqglbny66wpovyvao3ylc23eileodtevc4b75ikpad
     S: 250 OK

     C: ADD_ONION RSA1024:[Blob Redacted] Port=80,192.168.1.1:8080
     S: 250-ServiceID=sampleonion12456
     S: 250 OK

     C: ADD_ONION NEW:BEST Port=22 Port=80,8080
     S: 250-ServiceID=sampleonion4t2pqglbny66wpovyvao3ylc23eileodtevc4b75ikpad
     S: 250-PrivateKey=ED25519-V3:[Blob Redacted]
     S: 250 OK

     C: ADD_ONION NEW:RSA1024 Flags=DiscardPK,BasicAuth Port=22
        ClientAuth=alice:[Blob Redacted] ClientAuth=bob
     S: 250-ServiceID=testonion1234567
     S: 250-ClientAuth=bob:[Blob Redacted]
     S: 250 OK

     C: ADD_ONION NEW:ED25519-V3 ClientAuthV3=[Blob Redacted] Port=22
     S: 250-ServiceID=n35etu3yjxrqjpntmfziom5sjwspoydchmelc4xleoy4jk2u4lziz2yd
     S: 250-ClientAuthV3=[Blob Redacted]
     S: 250 OK
```
Examples with Tor in anonymous onion service mode:
```text
     C: ADD_ONION NEW:BEST Flags=DiscardPK Port=22
     S: 250-ServiceID=exampleoniont2pqglbny66wpovyvao3ylc23eileodtevc4b75ikpad
     S: 250 OK

     C: ADD_ONION NEW:BEST Flags=DiscardPK,NonAnonymous Port=22
     S: 512 Tor is in anonymous hidden service mode
```
Examples with Tor in non-anonymous onion service mode:
```text
     C: ADD_ONION NEW:BEST Flags=DiscardPK Port=22
     S: 512 Tor is in non-anonymous hidden service mode

     C: ADD_ONION NEW:BEST Flags=DiscardPK,NonAnonymous Port=22
     S: 250-ServiceID=exampleoniont2pqglbny66wpovyvao3ylc23eileodtevc4b75ikpad
     S: 250 OK
```

\[ADD_ONION was added in Tor 0.2.7.1-alpha.\]

\[MaxStreams and MaxStreamsCloseCircuit were added in Tor 0.2.7.2-alpha\]

\[ClientAuth was added in Tor 0.2.9.1-alpha. It is v2 only.\]

\[NonAnonymous was added in Tor 0.2.9.3-alpha.\]

\[HS v3 support added 0.3.3.1-alpha\]

\[ClientV3Auth support added 0.4.6.1-alpha\]

<a id="control-spec.txt-3.28"></a>

## DEL_ONION

The syntax is:

```text
    "DEL_ONION" SP ServiceID CRLF
    
    ServiceID = The Onion Service address without the trailing ".onion"
                suffix
```

Tells the server to remove an Onion ("Hidden") Service, that was
previously created via an "ADD_ONION" command.  It is only possible to
remove Onion Services that were created on the same control connection
as the "DEL_ONION" command, and those that belong to no control
connection in particular (The "Detach" flag was specified at creation).

If the ServiceID is invalid, or is neither owned by the current control
connection nor a detached Onion Service, the server will return a `552`.

It is the Onion Service server application's responsibility to close
existing client connections if desired after the Onion Service has been
removed via "DEL_ONION".

Tor replies with `250 OK` on success, or a `512` if there are an invalid
number of arguments, or a `552` if it doesn't recognize the ServiceID.

\[DEL_ONION was added in Tor 0.2.7.1-alpha.\]
\[HS v3 support added 0.3.3.1-alpha\]

<a id="control-spec.txt-3.29"></a>

## HSPOST

The syntax is:

```text
    "+HSPOST" *[SP "SERVER=" Server] [SP "HSADDRESS=" HSAddress]
              CRLF Descriptor CRLF "." CRLF

    Server = LongName
    HSAddress = 56*Base32Character
    Descriptor =  The text of the descriptor formatted as specified
                  in rend-spec.txt section 1.3.
```

The "HSAddress" key is optional and only applies for v3 descriptors. A `513`
error is returned if used with v2.

This command launches a hidden service descriptor upload to the specified
HSDirs. If one or more Server arguments are provided, an upload is triggered
on each of them in parallel. If no Server options are provided, it behaves
like a normal HS descriptor upload and will upload to the set of responsible
HS directories.

If any value is unrecognized, a `552` error is returned and the command is
stopped. If there is an error in parsing the descriptor, the server
must send a `554 Invalid descriptor` reply.

On success, Tor replies `250 OK` then Tor MUST eventually follow
this with an HS_DESC event with the result for each upload location.

Examples are:

```text
     C: +HSPOST SERVER=9695DFC35FFEB861329B9F1AB04C46397020CE31
        [DESCRIPTOR]
        .
     S: 250 OK

  [HSPOST was added in Tor 0.2.7.1-alpha]
```

<a id="control-spec.txt-3.30"></a>

## ONION_CLIENT_AUTH_ADD

The syntax is:

```text
    "ONION_CLIENT_AUTH_ADD" SP HSAddress
                            SP KeyType ":" PrivateKeyBlob
                            [SP "ClientName=" Nickname]
                            [SP "Flags=" TYPE] CRLF

    HSAddress = 56*Base32Character
    KeyType = "x25519" is the only one supported right now
    PrivateKeyBlob = base64 encoding of x25519 key
```

Tells the connected Tor to add client-side v3 client auth credentials for the
onion service with "HSAddress". The "PrivateKeyBlob" is the x25519 private
key that should be used for this client, and "Nickname" is an optional
nickname for the client.

FLAGS is a comma-separated tuple of flags for this new client. For now, the
currently supported flags are:

```text
    "Permanent" - This client's credentials should be stored in the filesystem.
                  If this is not set, the client's credentials are ephemeral
                  and stored in memory.
```

If client auth credentials already existed for this service, replace them
with the new ones.

If Tor has cached onion service descriptors that it has been unable to
decrypt in the past (due to lack of client auth credentials), attempt to
decrypt those descriptors as soon as this command succeeds.

On success, `250 OK` is returned. Otherwise, the following error codes exist:

- `251` - Client auth credentials for this onion service already existed and replaced.
- `252` - Added client auth credentials and successfully decrypted a cached descriptor.
- `451` - We reached authorized client capacity
- `512` - Syntax error in "HSAddress", or "PrivateKeyBlob" or "Nickname"
- `551` - Client with with this "Nickname" already exists
- `552` - Unrecognized KeyType

\[ONION_CLIENT_AUTH_ADD was added in Tor 0.4.3.1-alpha\]

<a id="control-spec.txt-3.31"></a>

## ONION_CLIENT_AUTH_REMOVE

The syntax is:
```text
    "ONION_CLIENT_AUTH_REMOVE" SP HSAddress CRLF
```

KeyType = "x25519" is the only one supported right now

Tells the connected Tor to remove the client-side v3 client auth credentials
for the onion service with "HSAddress".

On success `250 OK` is returned. Otherwise, the following error codes exist:

- `512` - Syntax error in "HSAddress".
- `251` - Client credentials for "HSAddress" did not exist.

\[ONION_CLIENT_AUTH_REMOVE was added in Tor 0.4.3.1-alpha\]


<a id="control-spec.txt-3.32"></a>

## ONION_CLIENT_AUTH_VIEW

The syntax is:

```text
    "ONION_CLIENT_AUTH_VIEW" [SP HSAddress] CRLF
```

Tells the connected Tor to list all the stored client-side v3 client auth
credentials for "HSAddress". If no "HSAddress" is provided, list all the
stored client-side v3 client auth credentials.

The server reply format is:

```text
    "250-ONION_CLIENT_AUTH_VIEW" [SP HSAddress] CRLF
    *("250-CLIENT" SP HSAddress SP KeyType ":" PrivateKeyBlob
                  [SP "ClientName=" Nickname]
                  [SP "Flags=" FLAGS] CRLF)
    "250 OK" CRLF

    HSAddress = The onion address under which this credential is stored
    KeyType = "x25519" is the only one supported right now
    PrivateKeyBlob = base64 encoding of x25519 key
```

"Nickname" is an optional nickname for this client, which can be set either
through the ONION_CLIENT_AUTH_ADD command, or it's the filename of this
client if the credentials are stored in the filesystem.

FLAGS is a comma-separated field of flags for this client, the currently
supported flags are:

"Permanent" - This client's credentials are stored in the filesystem.

On success `250 OK` is returned. Otherwise, the following error codes exist:

- `512` - Syntax error in "HSAddress".

\[ONION_CLIENT_AUTH_VIEW was added in Tor 0.4.3.1-alpha\]

<a id="control-spec.txt-3.33"></a>

## DROPOWNERSHIP

The syntax is:

```text
    "DROPOWNERSHIP" CRLF
```
This command instructs Tor to relinquish ownership of its control
connection. As such tor will not shut down when this control
connection is closed.

This method is idempotent. If the control connection does not
already have ownership this method returns successfully, and
does nothing.

The controller can call TAKEOWNERSHIP again to re-establish
ownership.

\[DROPOWNERSHIP was added in Tor 0.4.0.0-alpha\]

<a id="control-spec.txt-3.34"></a>

## DROPTIMEOUTS

The syntax is:
```text
    "DROPTIMEOUTS" CRLF
```

Tells the server to drop all circuit build times. Do not invoke this command
lightly; it can increase vulnerability to tracking attacks over time.

Tor replies with `250 OK` on success. Tor also emits the BUILDTIMEOUT_SET
RESET event right after this `250 OK`.

\[DROPTIMEOUTS was added in Tor 0.4.5.0-alpha.\]