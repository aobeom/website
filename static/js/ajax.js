/**
 * @author AoBeom
 * @create date 2017-12-08 16:15:17
 * @modify date 2018-07-07 22:16:44
 */


$(document).ready(function () {
    var uri = window.location.href.split("/")
    var aid = uri[uri.length - 1]
    $("#" + aid).addClass("active");
    $('#tipsbtn').click(function () {
        $('#tips').toggle();
    })
    var clipboard = new Clipboard('.btn');
    clipboard.on('success', function () {
        var tips = '<i class="fa fa-smile-o" aria-hidden="true"></i>&nbsp; Copied'
        $("#copied").html(tips)
    })
    if (uri[uri.length - 1] == "picture") {
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
        $('#picdown').click(function () {
            $('#picdown').attr({
                disabled: 'disabled'
            });
            $("#data").empty();
            var url = $("#picURL").val()
            var uri = ""
            var error_null = '<p class="btn btn-danger" onclick="location.reload();">URL ERROR / NO RESULT FOUND</p>';
            var error_system = '<p class="btn btn-danger" onclick="location.reload();">SYSTEM error</p>';
            if (url.length == 0) {
                $("#data").append(error_null);
                $('#picdown').removeAttr("disabled");
                return false;
            }
            var patrn = /http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
            var regex = new RegExp(patrn);
            if (regex.test(url) != true) {
                $("#data").append(error_null);
                $('#picdown').removeAttr("disabled");
                return false;
            } else {
                if (url.indexOf("showroom") != -1 || url.indexOf("line") != -1) {
                    uri = "/hls"
                } else {
                    uri = "/news"
                }
            }
            $.ajax({
                type: "GET",
                url: "/api/v1/media" + uri,
                data: "url=" + url,
                dataType: "json",
                success: function (msg) {
                    if (msg["status"] == 0) {
                        if (msg["data"]["type"] == "news") {
                            var urls = msg["data"]["entities"];
                            $("#data").empty();
                            for (u in urls) {
                                if (urls[u].indexOf(".mp4") > 0) {
                                    $('#data').append('<hr><p class="tools-img"><video src="' + urls[u] + '" controls="controls"></p>');
                                } else {
                                    $('#data').append('<hr><p class="tools-img"><img src="' + urls[u] + '"></p>');
                                }
                            }
                        }
                        if (msg["data"]["type"] == "hls") {
                            var urls = msg["data"]["entities"];
                            $("#data").empty();
                            $('#data').append('<p><button id="copied" class="btn btn-success" type="button" data-clipboard-text="' + urls + '"><i class="fa fa-clipboard" aria-hidden="true"></i>&nbsp; Copy to potplayer</button></p>');
                        }
                        $('#picdown').removeAttr("disabled");
                    } else {
                        $("#data").empty();
                        $('#data').append(error_null);
                        $('#picdown').removeAttr("disabled");
                    }
                },
                beforeSend: function () {
                    $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                },
                error: function () {
                    $("#data").empty();
                    $("#data").append(error_system);
                    $('#picdown').removeAttr("disabled");
                }
            });
        })
    } else if (uri[uri.length - 1] == "drama") {
        $.ajax({
            type: "GET",
            url: "/api/v1/drama/time",
            dataType: "json",
            success: function (msg) {
                var date = msg["data"]["time"]
                var countdown = msg["data"]["second"]
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
                $('#update').append('<span class="btn btn-info"><i class="fa fa-info-circle" aria-hidden="true"></i>&nbsp; Latest ' + date);
            },
        })
        $('.tools-btngroup button').click(function () {
            $("#data").empty();
            var data = {};
            var id = $(this).attr("id");
            error_system = '<p class="btn btn-danger" onclick="location.reload();">No drama data</p>'
            $.ajax({
                type: "GET",
                url: "/api/v1/drama/" + id,
                dataType: "json",
                success: function (msg) {
                    if (msg["status"] == 0) {
                        if (msg["data"]["name"] == "tvbt") {
                            var tvbt_data = msg["data"]["entities"];
                            $("#data").empty();
                            var tvbt_body = '<div class="accordion" id="dramapa">'
                            for (i in tvbt_data) {
                                var tvbts = tvbt_data[i];
                                var eps = tvbts["dlurls"];
                                var tvbt_title = '<div class="card tools-card"><div class="card-header" id="btn' + i + '" type="button" data-toggle="collapse" data-target="#tar' + i + '" aria-expanded="true" aria-controls="tar' + i + '"><span>' + tvbts["date"] + " - " + '</span><a href="' + tvbts["url"] + '" target="_blank">' + tvbts["title"] + '</a></div>';
                                var tvbt_ul = '<div id="tar' + i + '" class="collapse" aria-labelledby="btn' + i + '" data-parent="#dramapa"><div class="card-body tools-card-body"><div class="list-group"><a class="list-group-item list-group-item-action list-group-item-info">LINK#PASSWD</a>'
                                var tvbt_info = ""
                                for (j in eps) {
                                    var ep = eps[j];
                                    var tvbt_info = tvbt_info + '<a href="' + ep[1] + '#' + ep[2] + '" class="list-group-item list-group-item-action list-group-item-success" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; EP' + ep[0] + '</a>'
                                }
                                var tvbt_body = tvbt_body + tvbt_title + tvbt_ul + tvbt_info + '</div></div></div></div>';
                            }
                            $("#data").append(tvbt_body);
                        }
                        if (msg["data"]["name"] == "subpig") {
                            $("#data").empty();
                            var subpig_data = msg["data"]["entities"];
                            var subpig_body = '<div class="accordion" id="dramapa">';
                            for (i in subpig_data) {
                                var subpigs = subpig_data[i];
                                var eps = subpigs["dlurls"];
                                var subpig_title = '<div class="card tools-card"><div class="card-header" id="btn' + i + '" type="button" data-toggle="collapse" data-target="#tar' + i + '" aria-expanded="true" aria-controls="tar' + i + '"><span>' + subpigs["date"] + " - " + '</span><a href="' + subpigs["url"] + '" target="_blank">' + subpigs["title"] + '</a></div>';
                                var subpig_ul = '<div id="tar' + i + '" class="collapse" aria-labelledby="btn' + i + '" data-parent="#dramapa"><div class="card-body tools-card-body"><div class="list-group"><a class="list-group-item list-group-item-action list-group-item-info">LINK#PASSWD</a>'
                                var subpig_info = "";
                                if (typeof (eps) != "undefined") {
                                    var subpig_info = subpig_info + '<a href="' + eps[0] + '#' + eps[1] + '" class="list-group-item list-group-item-action list-group-item-success" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; BAIDU</a>';
                                }
                                var subpig_body = subpig_body + subpig_title + subpig_ul + subpig_info + '</div></div></div></div>';
                            }
                            $("#data").append(subpig_body);
                        }
                        if (msg["data"]["name"] == "fixsub") {
                            $("#data").empty();
                            var fixsub_data = msg["data"]["entities"];
                            var fixsub_body = '<div class="accordion" id="dramapa">';
                            for (i in fixsub_data) {
                                var fixsubs = fixsub_data[i]
                                var fixsub_title = '<div class="card tools-card"><div class="card-header" id="btn' + i + '" type="button" data-toggle="collapse" data-target="#tar' + i + '" aria-expanded="true" aria-controls="tar' + i + '"><span>' + '</span><a href="' + fixsubs["url"] + '" target="_blank">' + fixsubs["title"] + '</a></div>';
                                var fixsub_ul = '<div id="tar' + i + '" class="collapse" aria-labelledby="btn' + i + '" data-parent="#dramapa"><div class="card-body tools-card-body">';
                                var urls = fixsubs["dlurls"];
                                var fixsub_info_all = "";
                                for (j in urls) {
                                    var ep = urls[j];
                                    var fixsub_ep = '<div class="card-body tools-card-body"><div class="list-group"><a class="list-group-item list-group-item-action list-group-item-info">' + ep[0] + '</a>'
                                    var fixsub_info_b = fixsub_ep + '<a href="' + ep[1] + '" class="list-group-item list-group-item-action list-group-item-success" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; BAIDU</a>';
                                    var fixsub_info_m = fixsub_info_b + '<a href="' + ep[2] + '" class="list-group-item list-group-item-action list-group-item-success" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; MAGENT</a>';
                                    var fixsub_info_e = fixsub_info_m + '<a href="' + ep[3] + '" class="list-group-item list-group-item-action list-group-item-success" target="_blank"><i class="fa fa-link" aria-hidden="true"></i>&nbsp; ED2K</a>';
                                    var fixsub_info_all = fixsub_info_all + fixsub_info_e + '</div></div>';
                                }
                                var fixsub_body = fixsub_body + fixsub_title + fixsub_ul + fixsub_info_all + '</div></div></div>';
                            }
                            $("#data").append(fixsub_body)
                        }
                        $("a").each(function () {
                            if ($(this).text().length > 16) {
                                var text = $(this).text().substring(0, 16) + "...";
                                $(this).text(text);
                            }
                        })
                    } else {
                        $("#data").empty();
                        $('#data').append(error_system);
                    }
                    $('.tools-btngroup button').removeAttr("disabled");
                },
                beforeSend: function () {
                    $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                    $('.tools-btngroup button').attr({
                        disabled: "disabled"
                    });
                },
                error: function () {
                    $("#data").empty();
                    $("#data").append(error_system);
                    $('.tools-btngroup button').removeAttr("disabled");
                }
            });
        })
    } else if (uri[uri.length - 1] == "program") {
        $('#jprogram').click(function () {
            var keyword = $("#proKW").val()
            $('#jprogram').attr({
                disabled: 'disabled'
            });
            var code = $("#area").val()
            $("#data").empty();
            var error_null = '<p class="btn btn-danger" onclick="location.reload();">URL ERROR / NO RESULT FOUND</p>';
            var error_system = '<p class="btn btn-danger" onclick="location.reload();">SYSTEM error</p>';
            if (keyword.length == 0) {
                $("#data").append(error_null);
                $('#jprogram').removeAttr("disabled");
                return false;
            }
            $.ajax({
                type: "GET",
                url: "/api/v1/program",
                data: {
                    "kw": keyword,
                    "ac": code
                },
                dataType: "json",
                success: function (msg) {
                    if (msg["status"] == 0) {
                        $("#data").empty();
                        var purl = msg["ori_url"]
                        var pdata = msg["data"]["entities"]
                        var pdata_head = '<p><a class="btn btn-primary" href="' + purl + '" target="_blank">Yahoo Results</a></p>'
                        var pdata_body = ""
                        for (i in pdata) {
                            var pgram = pdata[i];
                            var pdata_date = pgram["date"]
                            var pdata_time = pgram["time"]
                            var pdata_url = pgram["url"]
                            var pdata_station = pgram["station"]
                            var pdata_title = pgram["title"]
                            var pdata_info = '<p><div><a class="btn btn-secondary" href="' + pdata_url + '" target="_blank"><p>' + pdata_date + "&nbsp; " + pdata_time + '</p><p>' + pdata_station + '</p><p>' + pdata_title + '</p></a></div><p>'
                            var pdata_content = pdata_date + pdata_time
                            var pdata_body = pdata_body + pdata_info
                        }
                        $('#jprogram').removeAttr("disabled");
                        $('#data').append(pdata_head + pdata_body);
                        $(".tools-load p").each(function (i) {
                            if ($(this).text().length > 16) {
                                var text = $(this).text().substring(0, 16) + "...";
                                $(this).text(text);
                            }
                        })
                    } else {
                        $("#data").empty();
                        $('#data').append(error_null);
                        $('#jprogram').removeAttr("disabled");
                    }
                },
                beforeSend: function () {
                    $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                },
                error: function () {
                    $("#data").empty();
                    $("#data").append(error_system);
                    $('#jprogram').removeAttr("disabled");
                }
            })
        })
    } else if (uri[uri.length - 1] == "stchannel") {
        var error_system = '<p class="btn btn-danger" onclick="location.reload();">SYSTEM error</p>';

        $.get("/api/v1/stchannel/time", function (msg) {
            if (msg["status"] == 0) {
                $(".btn-fresh").attr({
                    disabled: "disabled"
                });
            }
        })
        $('.btn-fresh').click(function () {
            $.post("/api/v1/stchannel/time", function (msg) {
                if (msg["status"] == 0) {
                    $(".btn-fresh").removeAttr('disabled');
                    location.reload();
                }
            })
        })
        $.ajax({
            type: "GET",
            url: "/api/v1/stchannel",
            dataType: "json",
            success: function (msg) {
                var st_body = ''
                $("#data").empty();
                if (msg["status"] == 0) {
                    var ut = msg["data"]["time"];
                    var dt = msg["data"]["entities"];
                    $('.btn-fresh').append('<i class="fa fa-info-circle" aria-hidden="true"></i>&nbsp; Latest ' + ut);
                    for (i in dt) {
                        var data = dt[i];
                        var s_date = data["date"];
                        var s_title = data["title"];
                        var s_murl = data["murl"];
                        var s_purl = data["purl"];
                        var s_id = "dlink" + i;
                        var st_info = '<hr><p>' + s_date + '</p><p style="text-align:left;">' + s_title + '</p><p class="tools-img"><img src="' + s_purl + '"></p><button id="' + s_id + '" class="btn btn-primary btn-source tools-button" value="' + s_murl + '">Resources</button>';
                        var st_body = st_body + st_info;
                    }
                } else {
                    st_body = '<span class="btn btn-danger">NO DATA</span>'
                }
                $('#data').append(st_body);
                $('.btn-source').click(function () {
                    var sid = $(this).attr("id")
                    var murl = {
                        "url": $(this).val()
                    }
                    $.ajax({
                        type: "POST",
                        contentType: "application/json;charset=utf-8",
                        url: "/api/v1/stchannel",
                        data: JSON.stringify(murl),
                        dataType: "json",
                        success: function (msg) {
                            var dl = '<a class="btn btn-success btn-source tools-button" href="' + msg["data"]["entities"] + '" target="_blank">Download</a>'
                            $("#" + sid).replaceWith(dl)
                            $(".tools-button").removeAttr("disabled");
                        },
                        beforeSend: function () {
                            $("#" + sid).text("Loading...")
                            $("#" + sid).attr({
                                disabled: "disabled"
                            });
                            $(".tools-button").attr({
                                disabled: "disabled"
                            });
                        },
                        error: function () {
                            $("#" + sid).replaceWith(error_system);
                        }
                    })
                })
            },
            beforeSend: function () {
                $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
            },
            error: function () {
                $("#data").empty();
                $('.btn-fresh').remove();
                $("#data").append(error_system);
            }
        })
    } else if (uri[uri.length - 1] == "tiktok") {
        $("#data").empty();
        var error_system = '<p class="btn btn-danger" onclick="location.reload();">SYSTEM error</p>';
        $.ajax({
            type: "GET",
            url: "/api/v1/tiktok",
            dataType: "json",
            success: function (msg) {
                var st_body = ''
                $("#data").empty();
                if (msg["status"] == 0) {
                    var dt = msg["data"]["entities"];
                    var ut = msg["data"]["time"];
                    $("#data").empty();
                    $('.btn-fresh').append('<i class="fa fa-info-circle" aria-hidden="true"></i>&nbsp; Latest ' + ut);
                    for (i in dt) {
                        var data = dt[i];
                        var s_date = data["time"];
                        var s_title = data["text"];
                        var s_murl = data["playlist"];
                        var s_purl = data["cover"];
                        var st_info = '<hr><p>' + s_date + '</p><p style="text-align:left;">' + s_title + '</p><p class="tools-img"><a href="' + s_murl + '" target="_blank"><img src="' + s_purl + '" style="width:200px"></a></p>';
                        var st_body = st_body + st_info;
                    }
                } else {
                    st_body = '<span class="btn btn-danger">NO DATA</span>'
                }
                $('#data').append(st_body);
            },
            beforeSend: function () {
                $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
            },
            error: function () {
                $("#data").empty();
                $('.btn-fresh').remove();
                $("#data").append(error_system);
            }
        })
    } else if (uri[uri.length - 1] == "rika") {
        var dsize = $(window).width();
        if (dsize <= 350) {
            var visible = 2;
        } else if (dsize >= 350 && dsize <= 700) {
            var visible = 3;
        } else if (dsize > 700) {
            var visible = 5;
        }
        $(".tools-btngroup button").click(function () {
            var typeid = $(this).attr("id");
            $("#pages").remove();
            $("#pagep").append('<div id="pages" class="tools-pages"></div>')
            $.ajax({
                type: "GET",
                url: "/api/v1/rikamsg",
                data: {
                    "type": typeid,
                },
                dataType: "json",
                success: function (page) {
                    var pages = page["data"]["pages"]
                    if (pages > 1) {
                        $("#pages").empty();
                        $("#data").empty();
                        $('#pages').twbsPagination({
                            totalPages: pages,
                            visiblePages: visible,
                            first: '<span aria-hidden="true">&laquo;&laquo;</span>',
                            prev: '<span aria-hidden="true">&laquo;</span>',
                            next: '<span aria-hidden="true">&raquo;</span>',
                            last: "Last " + pages,
                            onPageClick: function (event, page) {
                                $("#data").empty();
                                $.ajax({
                                    type: "GET",
                                    url: "/api/v1/rikamsg",
                                    data: {
                                        "page": page,
                                        "type": typeid,
                                    },
                                    dataType: "json",
                                    success: function (info) {
                                        msg = info["data"]["entities"]
                                        $("#data").empty();
                                        var body = '<div class="accordion" id="rikamsg">'
                                        for (i in msg) {
                                            message = msg[i]
                                            console.log(message)
                                            type = message["type"]
                                            date = message["date"]
                                            text = message["text"]
                                            media = message["media"]
                                            if (type == 1) {
                                                media_ele = '<img src="/media' + media + '" width="260px">'
                                            } else if (type > 1) {
                                                media_ele = '<video src="/media' + media + '" width="260px" controls="controls">'
                                            } else {
                                                media_ele = ''
                                            }
                                            var title = '<div class="card "><div class="card-header" id="btn' + i + '" type="button" data-toggle="collapse" data-target="#tar' + i + '" aria-expanded="true" aria-controls="tar' + i + '"><span>' + date + '</span></div>'
                                            var content = '<div id="tar' + i + '" class="collapse" aria-labelledby="btn' + i + '" data-parent="#rikamsg"><div class="card-body tools-msg"><span>' + text + '</span><div class="tools-media">' + media_ele + '</div></div></div>'
                                            var body = body + title + content + "</div>"
                                        }
                                        $("#data").append(body)
                                    },
                                    beforeSend: function () {
                                        $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                                    },
                                    error: function () {
                                        $("#data").append(error_system);
                                    }
                                })
                            }
                        });
                    } else {
                        $("#data").empty();
                        $.ajax({
                            type: "GET",
                            url: "/api/v1/rikamsg",
                            data: {
                                "page": 1,
                                "type": typeid,
                            },
                            dataType: "json",
                            success: function (info) {
                                msg = info["data"]["entities"]
                                $("#data").empty();
                                var body = '<div class="accordion" id="rikamsg">'
                                for (i in msg) {
                                    message = msg[i]["data"]["entities"]
                                    type = message["type"]
                                    date = message["date"]
                                    text = message["text"]
                                    media = message["media"]
                                    if (type == 1) {
                                        media_ele = '<img src="/media' + media + '" width="260px">'
                                    } else if (type > 1) {
                                        media_ele = '<video src="/media' + media + '" width="260px" controls="controls">'
                                    } else {
                                        media_ele = ''
                                    }
                                    var title = '<div class="card "><div class="card-header" id="btn' + i + '" type="button" data-toggle="collapse" data-target="#tar' + i + '" aria-expanded="true" aria-controls="tar' + i + '"><span>' + date + '</span></div>'
                                    var content = '<div id="tar' + i + '" class="collapse" aria-labelledby="btn' + i + '" data-parent="#rikamsg"><div class="card-body tools-msg"><span>' + text + '</span><div class="tools-media">' + media_ele + '</div></div></div>'
                                    var body = body + title + content + "</div>"
                                }
                                $("#data").append(body);
                                $("#pagep").empty();
                            },
                            beforeSend: function () {
                                $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                            },
                            error: function () {
                                $("#data").append(error_system);
                                $("#pagep").empty();
                            }
                        })
                    }
                },
            })
        })
    } else {
        var error_system = '<p class="btn btn-danger" onclick="location.reload();">SYSTEM error</p>';
        var error_size = '<p class="btn btn-danger" onclick="location.reload();">Must be less than 100M</p>';
        var error_type = '<p class="btn btn-danger" onclick="location.reload();">Only .mp4</p>';
        var success = '<p class="btn btn-success" onclick="location.reload();">Uploaded</p>';
        var uri = window.location.href.split("/")
        if (uri[uri.length - 1] == "hls") {
            $.ajax({
                type: "GET",
                url: "/api/v1/upload",
                dataType: "json",
                success: function (info) {
                    msg = info["data"]["number"]
                    $("#data").empty();
                    var vbody = '<ul class="list-group">'
                    for (i = 1; i < msg + 1; i++) {
                        var vlist = '<li class="list-group-item"><a href="/hls/' + i + '" target="_blank">video ' + i + '</a></li>'
                        var vbody = vbody + vlist + "</ul>"
                    }
                    $("#data").append(vbody)
                },
                beforeSend: function () {
                    $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                },
                error: function () {
                    $("#data").append(error_system);
                }
            })
        }
        $('#toolup').click(function () {
            $("#data").empty();
            var formData = new FormData();
            var filebody = $('#toolfile')[0].files[0]
            formData.append('file', filebody);
            var filevalue = $('#toolfile').val()
            if (filevalue == "") {
                $("#data").append(error_type);
                return false;
            }
            var filepath = filevalue.toLowerCase().split(".")
            var filesize = filebody.size
            var filetype = filepath[filepath.length - 1];
            var fileInfo = filevalue.split('\\');
            var fileName = fileInfo[fileInfo.length - 1];
            if (filesize > 102400000) {
                $("#data").append(error_size);
                return false;
            }
            if (filetype != "mp4") {
                $("#data").append(error_type);
                return false;
            }
            $.ajax({
                type: "POST",
                url: "/api/v1/upload",
                data: formData,
                processData: false,
                contentType: false,
                cache: false,
                dataType: "json",
                success: function (msg) {
                    $("#data").empty();
                    $("#data").append(success)
                },
                beforeSend: function () {
                    $("#data").empty();
                    $("#data").append('<p><i class="fa fa-cog fa-spin fa-3x fa-fw"></i></p>');
                },
                error: function () {
                    $("#data").empty();
                    $("#data").append(error_system);
                }
            })
        })
    }
})