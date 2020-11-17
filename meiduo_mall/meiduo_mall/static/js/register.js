// 采用ES6语法
// 创建Vue对象 vm

let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        // v-model
        username: "",
        password: '',
        password2: '',
        mobile: '',
        allow: null,

        // v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,

        // error_message
        error_name_message: "",
        error_mobile_message: '',
    },
    methods: {
        // 校验用户名
        check_username(){
            // 用户名5-20个字符
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            // 使用正则进行匹配
            if (re.test(this.username)) {
                // 匹配成功，不展示错误信息
                this.error_name = false;
            } else {
                // 匹配失败，展示错误信息
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }
        },
        // 校验密码
        check_password(){
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // 校验确认密码
        check_password2(){
            if(this.password != this.password2) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },
        // 校验手机号
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
        },
        // 校验是否勾选协议
        check_allow(){
            // 如果没有勾选，提示勾选信息
            if(!this.allow) {
                this.error_allow = true;
                // 如果勾选，不提示勾选信息
            } else {
                this.error_allow = false;
            }
        },
        // 监听表单提交事件
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();
            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if(this.error_name == true || this.error_password == true || this.error_password2 == true
                || this.error_mobile == true || this.error_allow == true) {
                // 禁用表单的提交
                window.event.returnValue = false;  // 阻止浏览器的默认行为（提交post请求），相当于return false;
            }
        },
    }
})