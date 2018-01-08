/**
 * @author AoBeom
 * @create date 2017-12-08 16:15:17
 * @modify date 2018-01-04 12:54:59
 */


$(document).ready(function () {
    $('#picdown').click(function () {
        $('#picdown').attr({
            disabled: 'disabled'
        });
        $("#datas").empty();
        var data = {
            "url": $("#picURL").val()
        };
        var error_null = '<p class="button-error pure-button" onclick="location.reload();">URL ERROR / NO RESULT FOUND</p>';
        var error_system = '<p class="button-error pure-button" onclick="location.reload();">SYSTEM error</p>';
        if (data["url"].length == 0) {
            $("#datas").append(error_null);
            $('#picdown').removeAttr("disabled");
            return false;
        }
        var patrn = /http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
        var regex = new RegExp(patrn);
        if (regex.test(data["url"]) != true) {
            $("#datas").append(error_null);
            $('#picdown').removeAttr("disabled");
            return false;
        }
        $.ajax({
            type: "POST",
            url: "/v1/api/picdown/",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(data),
            dataType: "json",
            success: function (msg) {
                if (msg["status"] == 0) {
                    if (msg["type"] == "picture") {
                        var urls = msg["datas"];
                        $("#datas").empty();
                        for (u in urls) {
                            $('#datas').append('<hr class="tools-hr"><p class="tools-img"><img src="' + urls[u] + '" style="width:300px"></p>');
                        }
                    }
                    if (msg["type"] == "m3u8") {
                        var urls = msg["datas"];
                        $("#datas").empty();
                        $('#datas').append('<p><button id="copied" class="button-success pure-button btn" type="button" data-clipboard-text="' + urls + '"><i class="fa fa-clipboard" aria-hidden="true"></i>&nbsp; Copy to potplayer</button></p>');
                    }
                    $('#picdown').removeAttr("disabled");
                } else {
                    $("#datas").empty();
                    $('#datas').append(error_null);
                    $('#picdown').removeAttr("disabled");
                }
            },
            beforeSend: function (XMLHttpRequest) {
                $("#datas").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
            },
            error: function () {
                $("#datas").empty();
                $("#datas").append(error_system);
                $('#picdown').removeAttr("disabled");
            }
        });
    })
});

$(document).ready(function () {
    $('#tipsbtn').click(function () {
        $('#tips').toggle();
    })
    var clipboard = new Clipboard('.btn');
    clipboard.on('success', function() {
        var tips = '<i class="fa fa-smile-o" aria-hidden="true"></i>&nbsp; Copied!'
        $("#copied").html(tips)
    })
    var uri = window.location.href.split("/")
    if (uri[uri.length - 1] == "drama") {
        $.ajax({
            type: "GET",
            url: "/v1/api/utime/",
            dataType: "json",
            success: function (msg) {
                var date = msg["message"]
                var countdown = msg["datas"]
                var sectotal = parseInt(countdown);

                function timer(sectotal) {
                    window.setInterval(function () {
                        var day = 0,
                            hour = 0,
                            minute = 0,
                            second = 0;
                        if (sectotal > 0) {
                            day = Math.floor(sectotal / (60 * 60 * 24));
                            hour = Math.floor(sectotal / (60 * 60)) - (day * 24);
                            minute = Math.floor(sectotal / 60) - (day * 24 * 60) - (hour * 60);
                            second = Math.floor(sectotal) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
                        }
                        if (minute <= 9) minute = '0' + minute;
                        if (second <= 9) second = '0' + second;
                        $('#drama_hour').text(hour + ' :');
                        $('#drama_minute').text(minute + ' :');
                        $('#drama_second').text(second);
                        sectotal--;
                    }, 1000);
                }
                $(function () {
                    timer(sectotal);
                });
                $('#update').append('<span class="button-span pure-button"><i class="fa fa-info-circle" aria-hidden="true"></i>&nbsp; Latest ' + date + ' JST');
            },
        })
    }
});

$(document).ready(function () {
    $('.tools-drama input').click(function () {
        $("#datas").empty();
        var data = {};
        var id = $(this).attr("id");
        var data = {
            "id": id
        };
        var error_system = '<p class="button-error pure-button" onclick="location.reload();">SYSTEM error</p>';
        $.ajax({
            type: "POST",
            url: "/v1/api/dramaget/",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(data),
            dataType: "json",
            success: function (msg) {
                if (msg["status"] == 0) {
                    if (msg["type"] == "tvbt") {
                        var tvbt_datas = msg["datas"];
                        $("#datas").empty();
                        var tvbt_body = ""
                        for (i in tvbt_datas) {
                            tvbts = tvbt_datas[i];
                            var tvbt_title = "";
                            tvbt_data = tvbt_datas[i];
                            eps = tvbts["dlurls"];
                            var tvbt_title = '<p><a class="button-secondary pure-button" href="' + tvbts["url"] + '" target="_blank">' + tvbts["date"] + ' - ' + tvbts["title"] + '</a></p>';
                            var tvbt_ul = '<div class="pure-menu pure-menu-scrollable custom-restricted tools-div"><span class="button-span pure-button tools-span">LINK#PASSWD</span><ul class="pure-menu-list">';
                            var tvbt_info = ""
                            for (j in eps) {
                                var ep = eps[j];
                                var tvbt_info = tvbt_info + '<li class="pure-menu-item"><a class="button-link pure-button tools-a" href="' + ep[1] + '#' + ep[2] + '" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; EP' + ep[0] + '</a></li>'
                            }
                            var tvbt_body = tvbt_body + tvbt_title + tvbt_ul + tvbt_info + '</ul></div>'
                        }
                        $("#datas").append(tvbt_body);
                    }
                    if (msg["type"] == "subpig") {
                        $("#datas").empty();
                        var subpig_datas = msg["datas"];
                        var subpig_body = "";
                        for (i in subpig_datas) {
                            subpigs = subpig_datas[i];
                            var subpig_title = "";
                            eps = subpigs["dlurls"];
                            var subpig_title = '<p><a class="button-secondary pure-button" href="' + subpigs["url"] + '" target="_blank">' + subpigs["date"] + ' - ' + subpigs["title"] + '</a></p>';
                            var subpig_ul = '<div class="pure-menu pure-menu-scrollable custom-restricted tools-div"><span class="button-span pure-button tools-span">LINK#PASSWD</span><ul class="pure-menu-list">';
                            var subpig_info = "";
                            if (typeof(eps) != "undefined"){
                                var subpig_info = subpig_info + '<li class="pure-menu-item"><a class="button-link pure-button tools-a" href="' + eps[0] + '#' + eps[1] + '" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; BAIDU</a></li>';
                            }
                            var subpig_body = subpig_body + subpig_title + subpig_ul + subpig_info + '</ul></div>';
                        }
                        $("#datas").append(subpig_body)
                    }
                    if (msg["type"] == "fixsub") {
                        $("#datas").empty();
                        var fixsub_datas = msg["datas"];
                        var fixsub_body = "";
                        for (i in fixsub_datas) {
                            fixsubs = fixsub_datas[i]
                            var fixsub_title = "";
                            fixsub_data = fixsub_datas[i];
                            var fixsub_title = '<p><a class="button-secondary pure-button" href="' + fixsubs["url"] + '" target="_blank">' + fixsubs["title"] + '</a></p>';
                            var fixsub_ul = '<div class="pure-menu pure-menu-scrollable custom-restricted tools-div"><ul class="pure-menu-list">';
                            var urls = fixsubs["dlurls"];
                            var fixsub_info_all = "";
                            for (j in urls) {
                                var ep = urls[j];
                                var fixsub_ep = '<li class="pure-menu-item"><span class="button-span pure-button tools-span">' + ep[0] + '</span></li>'
                                var fixsub_info_b = fixsub_ep + '<li class="pure-menu-item"><a class="button-link pure-button tools-a" href="' + ep[1] + '" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; Baidu</a></li>';
                                var fixsub_info_m = fixsub_info_b + '<li class="pure-menu-item"><a class="button-link pure-button tools-a" href="' + ep[2] + '" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; Magnet</a></li>';
                                var fixsub_info_e = fixsub_info_m + '<li class="pure-menu-item"><a class="button-link pure-button tools-a" href="' + ep[3] + '" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; ED2K</a></li>';
                                var fixsub_info_all = fixsub_info_all + fixsub_info_e
                            }
                            var fixsub_body = fixsub_body + fixsub_title + fixsub_ul + fixsub_info_all + '</ul></div>'
                        }
                        $("#datas").append(fixsub_body)
                    }
                    $("a").each(function () {
                        if ($(this).text().length > 16) {
                            var text = $(this).text().substring(0, 16) + "...";
                            $(this).text(text);
                        }
                    })
                } else {
                    $("#datas").empty();
                    $('#datas').append(error_system);
                }
                $('.tools-drama input').removeAttr("disabled");
            },
            beforeSend: function (XMLHttpRequest) {
                $("#datas").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                $('.tools-drama input').attr({
                    disabled: "disabled"
                });
            },
            error: function () {
                $("#datas").empty();
                $("#datas").append(error_system);
                $('.tools-drama input').removeAttr("disabled");
            }
        });
    })
});
$(document).ready(function () {
    $('#jprogram').click(function () {
        $('#jprogram').attr({
            disabled: 'disabled'
        });
        $("#datas").empty();
        var data = {
            "kw": $("#proKW").val()
        };
        var error_null = '<p class="button-error pure-button" onclick="location.reload();">URL ERROR / NO RESULT FOUND</p>';
        var error_system = '<p class="button-error pure-button" onclick="location.reload();">SYSTEM error</p>';
        if (data["kw"].length == 0) {
            $("#datas").append(error_null);
            $('#jprogram').removeAttr("disabled");
            return false;
        }
        $.ajax({
            type: "POST",
            url: "/v1/api/programget/",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify(data),
            dataType: "json",
            success: function (msg) {
                if (msg["status"] == 0) {
                    $("#datas").empty();
                    var purl = msg["message"]
                    var pdatas = msg["datas"]
                    var pdatas_head = '<p><a class="pure-button pure-button-primary" href="' + purl + '" target="_blank">Yahoo Results</a></p>'
                    var pdatas_body = ""
                    for (i in pdatas) {
                        var pgram = pdatas[i];
                        var pdatas_date = pgram["date"]
                        var pdatas_time = pgram["time"]
                        var pdatas_url = pgram["url"]
                        var pdatas_station = pgram["station"]
                        var pdatas_title = pgram["title"]
                        var pdatas_info = '<p><div><a class="button-div pure-button" href="' + pdatas_url + '" target="_blank"><p>' + pdatas_date + "&nbsp; " + pdatas_time + '</p><p>' + pdatas_station + '</p><p>' + pdatas_title + '</p></a></div><p>'
                        var pdatas_content = pdatas_date + pdatas_time
                        var pdatas_body = pdatas_body + pdatas_info
                    }
                    $('#jprogram').removeAttr("disabled");
                    $('#datas').append(pdatas_head + pdatas_body);
                    $(".tools-load p").each(function (i) {
                        if ($(this).text().length > 18) {
                            var text = $(this).text().substring(0, 18) + "...";
                            $(this).text(text);
                        }
                    })
                } else {
                    $("#datas").empty();
                    $('#datas').append(error_null);
                    $('#jprogram').removeAttr("disabled");
                }
            },
            beforeSend: function (XMLHttpRequest) {
                $("#datas").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
            },
            error: function () {
                $("#datas").empty();
                $("#datas").append(error_system);
                $('#jprogram').removeAttr("disabled");
            }
        })
    })
})

$(document).ready(function () {
    var segmentWidth = 0;
    $(".tools-banner .tools-banner-content li").each(function () {
        segmentWidth += $(this).outerWidth(true);
    });

    $(".tools-banner .tools-banner-content li").clone().appendTo($(".tools-banner .tools-banner-content"));

    run(6000);

    function run(interval) {
        $(".tools-banner .tools-banner-content").animate({
            "left": -segmentWidth
        }, interval, "linear", function () {
            $(".tools-banner .tools-banner-content").css("left", 0);
            run(6000);
        });
    }

    $(".tools-banner").mouseenter(function () {
        $(".tools-banner .tools-banner-content").stop();
    }).mouseleave(function () {
        var passedCourse = -parseInt($(".tools-banner .tools-banner-content").css("left"));
        var time = 6000 * (1 - passedCourse / segmentWidth);
        run(time);
    });
})