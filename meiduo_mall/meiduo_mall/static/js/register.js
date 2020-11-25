// 采用ES6语法
// 创建Vue对象 vm
// 短信验证码前端不校验对错，只校验是否是6位数字，提交表单后，由后端校验并返回结果
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
        image_code: '',
        sms_code: '',

        // v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        // 模板变量
        error_name_message: "",
        error_mobile_message: '',
        error_image_code_message: '',
        sms_code_tip: '获取短信验证码',  // 短息验证码提示信息
        error_sms_code_message: '',

        // v-bind
        image_code_url: "",  // 图片验证码url
        uuid : '',  // uuid

        send_sms_flag: false,  // 是否可以发送短信验证码

        // 检查是否完成填写
        username_done: false,
        password_done: false,
        password2_done: false,
        mobile_done: false,
        allow_done: false,
        image_code_done: false,
        sms_code_done: false,
    },

    // 页面加载完成时，该方法会被调用，即模板第一次渲染完成后，vue会先对data中的模板变量进行渲染
    mounted(){
        // 页面加载完成后，生成图片验证码
        this.generate_image_code_url();
    },
    methods: {
        check_all_is_done(){
          if(this.username_done === true && this.password_done === true && this.password2_done === true &&
              this.mobile_done === true && this.allow_done === true && this.image_code_done === true
              && this.sms_code_done === true){
                // 更改注册按钮样式
                this.activate_sub_input();
          }
        },
        activate_sub_input(){
            let sub_input = $('#sub_input');
            sub_input.css({backgroundColor: '#ff5757', cursor: 'pointer'});
        },
        deactivate_sub_input(){
            let sub_input = $('#sub_input');
            sub_input.css({backgroundColor: '#5e5c5c', cursor: 'auto'});
        },
        send_sms_code(){
            // 发送短信验证码
            // 避免恶意用户频繁的点击获取短信验证码
            if(this.send_sms_flag === true){
                return;
            }
            this.send_sms_flag = true;
            // 校验数据：mobile，image_code，避免用户没有输入手机号与短信验证码，就可以发送ajax请求
            this.check_mobile();
            this.check_image_code();
            if(this.error_mobile === true || this.error_image_code === true){
                this.send_sms_flag = false;  // 数据有问题，可以重新发送短信验证码
                return;
            }
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url,{
                responseType: 'json',
            })
                .then(response =>{
                    // 发送短信验证码成功
                    if(response.data.code === '0'){
                        // 展示60秒倒计时
                        let num = 60;
                        let time = setInterval(()=>{
                            // 倒数计时结束，可重新发送验证码
                            if(num === 0){
                                clearInterval(time);
                                this.sms_code_tip = '获取短信验证码'; // 还原提示信息
                                this.generate_image_code_url();  // 重新生成图形验证码
                                this.send_sms_flag = false;  // 发送成功后，可重新发送短信验证码
                            } else{  // 显示倒计时
                                $('#sms_code_a').css('cursor', 'auto');
                                num -= 1;
                                this.sms_code_tip = num + '秒后重新发送';
                            }
                        }, 1000)
                    } else{
                        // '4010'  图形验证码过期      '4001'  图形验证码错误
                        if(response.data.code === '4001' || response.data.code === '4010') {
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                            this.send_sms_flag = false;  // 图形验证码出现错误，可重新发送短信
                        }
                    }
                })
                .catch(error => {
                    console.log(error.response)
                    this.send_sms_flag = false  // 出现错误，可重新发送短信
            })
        },
        // 生成图片验证码与url
        generate_image_code_url(){
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },
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
                this.username_done = false;
                this.deactivate_sub_input();
            }
            // 校验用户名是否存在
            // 只有匹配成功，输入的用户名符合条件才进行判断
            if (this.error_name === false){
                // url只写路径，从根路径开始写
                let url = `/usernames/${this.username}/count/`;
                axios.get(url, {
                    responseType: 'json',
                })
                    .then((response)=>{
                        if(response.data.count === 1){
                            // 用户名已存在
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                            this.username_done = false;
                            this.deactivate_sub_input();
                        } else{
                            // 用户名不存在
                            this.error_name = false;
                            // 检查是否填写完成
                            this.username_done = true;
                            this.check_all_is_done();
                        }

                    })
                    .catch(error=>{
                        console.log(error.response);
                    })
            }
        },
        // 校验密码
        check_password(){
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
                // 检查是否填写完成
                this.password_done = true;
                this.check_all_is_done();
            } else {
                this.error_password = true;
                this.password_done = false;
                this.deactivate_sub_input();
            }
        },
        // 校验确认密码
        check_password2(){
            if(this.password !== this.password2) {
                this.error_password2 = true;
                this.password2_done = false;
                this.deactivate_sub_input();
            } else {
                this.error_password2 = false;
                // 检查是否填写完成
                this.password2_done = true;
                this.check_all_is_done();
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
                this.mobile_done = false;
                this.deactivate_sub_input();
            }
            // 校验手机号是否存在
            // 只有匹配成功，输入的手机号符合条件才进行判断
            if (this.error_mobile === false){
                // url只写路径，从根路径开始写
                let url = `/mobiles/${this.mobile}/count/`;
                axios.get(url, {
                    responseType: 'json',
                })
                    .then((response)=>{
                        if(response.data.count === 1){
                            // 手机号已存在
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                            this.mobile_done = false;
                            this.deactivate_sub_input();
                        } else{
                            // 手机号不存在
                            this.error_mobile = false;
                            // 检查是否填写完成
                            this.mobile_done = true;
                            this.check_all_is_done();
                        }

                    })
                    .catch(error=>{
                        console.log(error.response);
                    })
            }
        },
        // 校验图形验证码
        check_image_code(){
            if(this.image_code.length !== 4){
                this.error_image_code_message = '请输入4位图形验证码';
                this.error_image_code = true;
                this.image_code_done = false;
                this.deactivate_sub_input();
            } else{
                let re = /^[0-9a-zA-Z]{4}/;
                if(re.test(this.image_code)){
                    this.error_image_code = false;
                    // 检查是否填写完成
                    this.image_code_done = true;
                    this.check_all_is_done();
                } else{
                    this.error_image_code_message = '请输入4为有效图形验证码';
                    this.error_image_code = true;
                    this.image_code_done = false;
                    this.deactivate_sub_input();
                }

            }

        },
        // 校验短信验证码
        check_sms_code(){
            // 如果未填写短信验证码
            if(this.sms_code.length === 0){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
                this.sms_code_done = false;
                this.deactivate_sub_input();
                // 填写了短信验证码
            } else{
                let re = /^\d{6}$/;
                // 是否是6位数字的短信验证码
                if(re.test(this.sms_code)){
                    this.error_sms_code = false;
                    // 检查是否填写完成
                    this.sms_code_done = true;
                    this.check_all_is_done();
                } else{
                    this.error_sms_code_message = '请填写有效的6位短信验证码';
                    this.error_sms_code = true;
                    this.sms_code_done = false;
                    this.deactivate_sub_input();
                }
            }

        },
        // 校验是否勾选协议
        check_allow(){
            // 如果没有勾选，提示勾选信息
            if(!this.allow) {
                this.error_allow = true;
                this.allow_done = false;
                this.deactivate_sub_input();
                // 如果勾选，不提示勾选信息
            } else {
                this.error_allow = false;
                // 检查是否填写完成
                this.allow_done = true;
                this.check_all_is_done();
            }
        },
        // 监听表单提交事件
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_image_code();
            this.check_sms_code();
            this.check_allow();
            // 在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if(this.error_name === true || this.error_password === true || this.error_password2 === true ||
                this.error_mobile === true || this.error_allow === true || this.error_image_code === true ||
                this.error_sms_code === true) {
                // 禁用表单的提交
                // 阻止浏览器的默认行为（提交post请求），相当于return false;
                window.event.returnValue = false;
            }
            this.username_done = false;
            this.password_done = false;
            this.password2_done = false;
            this.mobile_done = false;
            this.allow_done = false;
            this.image_code_done = false;
            this.sms_code_done = false;
        },
    }
})