/*  公共方法  */
    //格式化日期函数
function formatDate(myDate) {
    var formatTime = myDate.getFullYear() + "-";
    var m = myDate.getMonth()+1,
        d = myDate.getDate();
    if (m >= 10) {
        formatTime += m + '-';
    }else {
        formatTime += '0' + m + '-';
    }
    if (d >= 10) {
        formatTime += d;
    }else{
        formatTime += '0' + d;
    }
    return formatTime;
}
    // 方法:获得N天前的日期   dayNumber:新增天数  date：开始日期,没传默认今天
function addDay(dayNumber, date) {
    date = date ? date : new Date();
    var ms = dayNumber * (1000 * 60 * 60 * 24);
    var newDate = new Date(date.getTime() - ms);
    return formatDate(new Date(newDate));
}
    //数组求和
function Sum(dataArr) {
    var sum = 0;
    for(var i=0; i<dataArr.length; i++){
        sum += parseInt(dataArr[i]);
    }
    return sum;
}
    // 当前time: '2016-2-1' ==> '2016-02-01'
function formatMD(time) {
    var theTime = time.split('-');
    var month = theTime[1];
    var day = theTime[2];
    var forTime = theTime[0]+'-';
    if (month >= 10){
        forTime += month + '-';
    }else{
        forTime += '0' + month + '-';
    }
    if (day >= 10){
        forTime += day;
    }else {
        forTime += '0' + day
    }
    return forTime;
}


var amountText = '成交金额';
var orderCountText = '支付订单数';
var userRegCountText = '用户注册数';
var userTextTit = '注册用户类型';
var userText = '注册来源';


//初始化 成交金额 echarts 折线图实例
var amountChart = echarts.init(document.getElementById('amount_chart'));
amountChart.showLoading();

//初始化 支付订单数 echarts 折线图实例
var orderCountChart = echarts.init(document.getElementById('orderCount_chart'));
orderCountChart.showLoading();

//初始化 注册数量 echarts 折线图实例
var userRegCountChart = echarts.init(document.getElementById('userRegCount_chart'));
userRegCountChart.showLoading();

//初始化 注册用户类型 echarts饼状图实例
var userChart = echarts.init(document.getElementById('user_chart'));
userChart.showLoading();

//可共用的 [折线图] 配置参数
var option = {
    title: {
        text: '',
        left: '5%',
        textStyle:{
            color: '#666',
            fontSize: '20',
            fontWeight: 'bold',
            fontStyle: 'italic'
        }
    },
    tooltip: {
        trigger: 'axis'
    },
    legend: {
        data:['all-platform','IOS','Android','H5','PC']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },

    xAxis: {
        type: 'category',
        boundaryGap: false,
        data: []
    },
    yAxis: {
        type: 'value'
    },
    series: [
        {
            name:'all-platform',
            type:'line',
            //stack: '总量',
            data:[]
        },
        {
            name:'IOS',
            type:'line',
            //stack: '总量',
            data:[]
        },
        {
            name:'Android',
            type:'line',
            //stack: '总量',
            data:[]
        },
        {
            name:'H5',
            type:'line',
            //stack: '总量',
            data:[]
        },
        {
            name:'PC',
            type:'line',
            //stack: '总量',
            data:[]
        }
    ]
};

//饼状图
var userOption = {
    title : {
        text: userTextTit,
        subtext: 'Motif',
        x:'center'
    },
    tooltip : {
        trigger: 'item',
        formatter: "{a} <br/>{b} : {c} ({d}%)"
    },
    legend: {
        orient: 'vertical',
        left: 'left',
        data: []
    },
    series : [
        {
            name: userText,
            type: 'pie',
            radius : '55%',
            center: ['50%', '60%'],
            data:[],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
    ]
};

$(function(){
    //填入 顶部概览表格数据
    $.getJSON('http://dashboard.motif.me/new/headData', function (data) {
        $('.old-amount').html(data.order_res.yesterday_amount);
        $('.old-order').html(data.order_res.yesterday_count);
        $('.old-user').html(data.userReg_res.yesterday_count);

        $('.today-amount').html(data.order_res.today_amount);
        $('.today-order').html(data.order_res.today_count);
        $('.today-user').html(data.userReg_res.today_count);
    });
    //初始化日期控件
    $('#dateInput-amount').daterangepicker({
        arrows:true
    });
    $('#dateInput-count').daterangepicker({
        arrows:true
    });
    $('#dateInput-user').daterangepicker({
        arrows:true
    });

    //初始化折线图数据: 成交金额 & 支付订单数  -- 默认显示近7天的数据
    var currentDate = formatDate(new Date());//获取今天日期
    var beforeDate7 = addDay(7);
    getAmount(beforeDate7,currentDate);
    getOrderCount(beforeDate7,currentDate);
    getUserCount(beforeDate7,currentDate);
    getSkuRank();

    $('.queryBtn-amount').on('click', function () {
        var dateStr = $('#dateInput-amount').val();
        console.warn(dateStr);
        dateStr = dateStr.split(' ~ ');
        var startTime = formatMD(dateStr[0]);
        var endTime = formatMD(dateStr[1]);
        getAmount(startTime, endTime);
    });

    $('.queryBtn-orderCount').on('click', function () {
        var dateStr = $('#dateInput-count').val();
        dateStr = dateStr.split(' ~ ');
        var startTime = formatMD(dateStr[0]);
        var endTime = formatMD(dateStr[1]);
        getOrderCount(startTime, endTime);
    });

    $('.queryBtn-userCount').on('click', function () {
        var dateStr = $('#dateInput-user').val();
        dateStr = dateStr.split(' ~ ');
        var startTime = formatMD(dateStr[0]);
        var endTime = formatMD(dateStr[1]);
        getUserCount(startTime, endTime);
    });
    
    
});


// ajax请求加载 -- 成交金额数据
function getAmount(startTime, endTime) {
    $.ajax({
        type: "GET",
        url: 'http://dashboard.motif.me/new/orderQuery',
        data: {
            stt: startTime,
            edt: endTime
        }
    }).done(function (data) {
        var objData = JSON.parse(data);
        amountChart.hideLoading();
        
        var iosTm = Sum(objData.ios_amount),
            androidTm = Sum(objData.android_amount),
            h5Tm = Sum(objData.h5_amount),
            pcTm = Sum(objData.pc_amount);
        $('.all-tm').html(iosTm+androidTm+h5Tm+pcTm);
        $('.ios-tm').html(iosTm);
        $('.android-tm').html(androidTm);
        $('.h5-tm').html(h5Tm);
        $('.pc-tm').html(pcTm);
        var ap_amount=new Array();
        for(var _i=0;_i<objData.ios_count.length;_i++){
            ap_amount[_i]=(objData.ios_amount[_i]+objData.android_amount[_i]+objData.h5_amount[_i]+objData.pc_amount[_i]).toFixed(2);
        }
        //填入echart数据
        amountChart.setOption({
            title: {
                text: amountText
            },
            xAxis: {
                data: objData.datetime
            },
            series:[{
                name: 'all-platform',
                data: ap_amount
            },{
                name: 'IOS',
                data: objData.ios_amount
            },{
                name: 'Android',
                data: objData.android_amount
            },{
                name: 'H5',
                data: objData.h5_amount
            },{
                name: 'PC',
                data: objData.pc_amount
            }]
        });
    });
    amountChart.setOption(option);
}


// ajax请求加载 -- 支付订单数 数据
function getOrderCount(startTime, endTime) {
    $.ajax({
        type: "GET",
        url: 'http://dashboard.motif.me/new/orderQuery',
        data: {
            stt: startTime,
            edt: endTime
        }
    }).done(function (data) {
        var objData = JSON.parse(data);
        orderCountChart.hideLoading();
        
        var iosCount = Sum(objData.ios_count),
            androidCount = Sum(objData.android_count),
            h5Count = Sum(objData.h5_count),
            pcCount = Sum(objData.pc_count);
        $('.all-count').html(iosCount+androidCount+h5Count+pcCount);
        $('.ios-count').html(iosCount);
        $('.android-count').html(androidCount);
        $('.h5-count').html(h5Count);
        $('.pc-count').html(pcCount);

        var ap_count=new Array();
        for(var _i=0;_i<objData.ios_count.length;_i++){
            ap_count[_i]=(objData.ios_count[_i]+objData.android_count[_i]+objData.h5_count[_i]+objData.pc_count[_i]);
        }
        //填入echart数据
        orderCountChart.setOption({
            title: {
                text: orderCountText
            },
            xAxis: {
                data: objData.datetime
            },
            series:[{
                name: 'all-platform',
                data: ap_count
            },{
                name: 'IOS',
                data: objData.ios_count
            },{
                name: 'Android',
                data: objData.android_count
            },{
                name: 'H5',
                data: objData.h5_count
            },{
                name: 'PC',
                data: objData.pc_count
            }]
        });
    });
    orderCountChart.setOption(option);
}

// ajax请求加载 -- 注册用户数 数据
function getUserCount(startTime, endTime) {
    //  http://dashboard.motif.me/new/userQuery/?stt=2016-08-01&edt=2016-10-10
    $.ajax({
        type: "GET",
        url: 'http://dashboard.motif.me/new/userQuery',
        data: {
            stt: startTime,
            edt: endTime
        }
    }).done(function (data) {
        var objData = JSON.parse(data);
        //console.log(objData.datetime);
        userChart.hideLoading();
        userRegCountChart.hideLoading();
        //处理数据
        var userDataArr = objData.login_distribute;
        var legendData = []; //来源名称的数组
        var userCountDate = []; //来源对应的数量
        for(var i=0; i<userDataArr.length; i++){
            legendData.push(userDataArr[i].name);
            userCountDate.push(userDataArr[i].value);
            //得到数据 填入html标签中
            if (userDataArr[i].value){
                if (userDataArr[i].name == 'email'){
                    $('.user-email').html(userDataArr[i].value)
                }else if (userDataArr[i].name == 'facebook'){
                    $('.user-fb').html(userDataArr[i].value);
                }else if (userDataArr[i].name == 'google'){
                    $('.user-gg').html(userDataArr[i].value);
                }
            }else {
                $('.user-email').html(0);
                $('.user-fb').html(0);
                $('.user-gg').html(0);
            }
        }
        $('.user-all').html(Sum(userCountDate));

        userChart.setOption({
            legend: {
                orient: 'vertical',
                left: 'left',
                data:  legendData
            },
            series : [
                {
                    name: userText,
                    type: 'pie',
                    radius : '55%',
                    center: ['50%', '60%'],
                    data: userDataArr,
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        });
        userRegCountChart.setOption({
            title: {
                text: userRegCountText
            },
            xAxis: {
                data: objData.datetime
            },
            series:[{
                name: 'all-platform',
                data: objData.reg_count
            },{
                name: 'IOS',
                data: []
            },{
                name: 'Android',
                data: []
            },{
                name: 'H5',
                data: []
            },{
                name: 'PC',
                data: []
            }]
        });
    });

    userRegCountChart.setOption(option);
    userChart.setOption(userOption);
}

function getSkuRank() {
        $.getJSON('http://dashboard.motif.me/new/skuRank/', {}, function ($jsondata) {
            this.colume_name = $jsondata.colume_name;
            this.row = $jsondata.row;
            drawSkuRankTable($jsondata);
        });

}
function drawSkuRankTable ($jsondata) {
    var html = '<table border=1>';


    var obj = $jsondata.rank_res;
    console.log('obj==='+obj);


    html += '<tr>'
    html += '<td style="width:70px; text-align:center">' + 'id' + '</td>'
    for(var i in obj.column_name)
    {
        if(obj.column_name[i]=='标题')
            html += '<td style="width:150px; text-align:center">' + obj.column_name[i] + '</td>';

        else
            html += '<td style="width:70px; text-align:center">' + obj.column_name[i] + '</td>';
    }
    html += '</tr>'
    row=obj.row
    // console.log(row);

    for( var z in  row)
    {    html += '<tr>'
        //console.log('zzz'+z);
        _row=obj.row[z]
        // console.log('每一行'+_row)
        for(var y in _row)
        {   //console.log('每个单元'+_row[y]);
            //console.log('每个y'+y);
            html += '<td style="width:70px; text-align:center">';
            if(y==9)
                _row[y]='<img src='+'http://image.motif.me/n4/'+_row[y]+' width="90px" height="90px">'
            html +=  _row[y]==null?'':_row[y] + '</td>';
        }
        html += '</tr>'
    }
    html += '</table>';
    //console.log(html);
    $('.skuRank').append(html);
}