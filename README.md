gotld
=====

Get domain's tld in golang. Updated to support translation between IDN ccTLDs and their
Punycode representations.


## Install gotld

    go get github.com/sourcekris/gotld

## Import gotld

    import "github.com/sourcekris/gotld"


## Use gotld

For example.

    tld, domain, err := gotld.GetTld("www.abc.xn--fiqz9s")
    if err != nil {
        fmt.Println( err )
        return
    }
    fmt.Printf( "TLD: %s, Domain: %s\n", tld.Tld, domain )

## About Original Author:

    北京实易时代科技有限公司
    Beijing ForEase Times Technology Co., Ltd.
    http://www.forease.net
    Jonsen Yang
    im16hot#gmail.com (replace # with @)

## Original Repo

  github.com/sourcekris/gotld

