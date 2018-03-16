/**
 * Created by lenovo on 2018-03-15.
 */
 //add by zhs 20151027 下载文书
    function DownLoadCase(caseInfo) {
        var thebody = document.body;
        var formid = 'DownloadForm';
        var url = '/CreateContentJS/CreateListDocZip.aspx?action=1';
        var theform = document.createElement('form');
        theform.id = formid;
        theform.action = url;
        theform.method = 'POST';
        theform.target = "_blank";
        //获取检索条件，作为压缩包名称
        var $conditions = $(".removeCondtion");
        var conditions = "";
        $conditions.each(function () {
            conditions += $(this).attr("val") + "&";
        });
        conditions = conditions.substr(0, conditions.length - 1);
        conditions = conditions.replace(/:/g, "为").replace(/&/g, "且");

        var theInput = document.createElement('input');
        theInput.type = 'hidden';
        theInput.id = 'conditions';
        theInput.name = 'conditions';
        theInput.value = encodeURI(conditions);
        theform.appendChild(theInput);

        var theInput = document.createElement('input');
        theInput.type = 'hidden';
        theInput.id = 'docIds';
        theInput.name = 'docIds';
        theInput.value = caseInfo;
        theform.appendChild(theInput);

        //验证码功能暂未启用
        var theInput = document.createElement('input');
        theInput.type = 'hidden';
        theInput.id = 'keyCode';
        theInput.name = 'keyCode';
        theInput.value = '';
        theform.appendChild(theInput);

        thebody.appendChild(theform);
        theform.submit();
    }

//列表页下载单篇文书
    function DownLoadCase(caseInfo) {
        var thebody = document.body;
        var formid = 'DownloadForm';
        var url = '/CreateContentJS/CreateListDocZip.aspx?action=1';
        var theform = document.createElement('form');
        theform.id = formid;
        theform.action = url;
        theform.method = 'POST';

        var theInput = document.createElement('input');
        theInput.type = 'hidden';
        theInput.id = 'docIds';
        theInput.name = 'docIds';
        theInput.value = caseInfo;
        theform.appendChild(theInput);

        //验证码功能暂未启用
        var theInput = document.createElement('input');
        theInput.type = 'hidden';
        theInput.id = 'keyCode';
        theInput.name = 'keyCode';
        theInput.value = '';
        theform.appendChild(theInput);

        thebody.appendChild(theform);
        theform.submit();
    }