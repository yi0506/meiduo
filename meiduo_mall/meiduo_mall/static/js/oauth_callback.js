let vm = new Vue({
	el: '#app',
    delimiters: ['[[', ']]'],
	data: {
		mobile: '',
		password: '',
		image_code: '',
		sms_code: '',

		error_mobile: false,
		error_password: false,
		error_image_code: false,
		error_sms_code: false,

		error_mobile_message: '',
		error_image_code_message: '',
		error_sms_code_message: '',

		uuid: '',
		image_code_url: '',
		sms_code_tip: '获取短信验证码',
		sending_flag: false,

		// 检查每一项是否完成填写
        password_done: false,
        mobile_done: false,
        image_code_done: false,
        sms_code_done: false,
	},
	mounted(){
		// 生成图形验证码
		this.generate_image_code();
	},
	methods: {
		// 检查表单是否填写完成
		check_all_is_done(){
          if(this.password_done === true && this.mobile_done === true
			  && this.image_code_done === true && this.sms_code_done === true){
                // 更改注册按钮样式
                this.activate_sub_input();
          }
        },
		// 激活注册按钮
        activate_sub_input(){
            let oauth_input = $('#oauth_input');
            oauth_input.css({backgroundColor: '#ff5757', cursor: 'pointer'});
        },
		// 反激活注册按钮
        deactivate_sub_input(){
            let oauth_input = $('#oauth_input');
            oauth_input.css({backgroundColor: '#5e5c5c', cursor: 'auto'});
        },
		// 生成图形验证码
		generate_image_code(){
			this.uuid = generateUUID();
			this.image_code_url = "/image_codes/" + this.uuid + "/";
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
		// 检查密码
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
		// 发送短信验证码
		send_sms_code(){
			// 避免频繁点击发送短信验证码标签
			if (this.sending_flag === true) {
				return;
			}
			this.sending_flag = true;

			// 校验参数
			this.check_mobile();
			this.check_image_code();
			if (this.error_mobile === true || this.error_image_code === true) {
				this.sending_flag = false;
				return;
			}

			// 向后端接口发送请求，让后端发送短信验证码
			let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code+'&uuid='+ this.uuid;
			axios.get(url, {
				responseType: 'json'
			})
				.then(response => {
					// 表示后端发送短信成功
					if (response.data.code === '0') {
						// 倒计时60秒
						let num = 60;
						let t = setInterval(() => {
							if (num == 1) {
								clearInterval(t);
								this.sms_code_tip = '获取短信验证码';
								this.generate_image_code();
								this.sending_flag = false;
							} else {
								num -= 1;
								this.sms_code_tip = num + '秒';
							}
						}, 1000)
					} else {
						if (response.data.code === '4001') {
							this.error_image_code_message = response.data.errmsg;
							this.error_image_code = true;
                        } else { // 4002
							this.error_sms_code_message = response.data.errmsg;
							this.error_sms_code = true;
						}
						this.sending_flag = false;
					}
				})
				.catch(error => {
					console.log(error.response);
					this.sending_flag = false;
				})
		},
		// 绑定openid
		on_submit(){
			this.check_mobile();
			this.check_password();
			this.check_sms_code();
			this.check_image_code();

			if(this.error_mobile === true || this.error_password === true ||
				this.error_sms_code === true || this.error_image_code === true) {
				// 不满足条件：禁用表单提交
				return false;
			}
            this.password_done = false;
            this.mobile_done = false;
            this.image_code_done = false;
            this.sms_code_done = false;
		}
	}
});