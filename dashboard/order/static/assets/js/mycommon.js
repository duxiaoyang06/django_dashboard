(function ($) {
    //加载 共用的部分到各个页面
    $('.common-parts').load('navigation.html');
    //Menu 改变页面窗口的大小时, 侧边导航的显示与隐藏
    $(window).on("resize", function () {
        if ($(this).width() < 768) {
            $('div.sidebar-collapse').addClass('collapse')
        } else {
            $('div.sidebar-collapse').removeClass('collapse')
        }
    });

})(jQuery);
