'use strict'

import React from 'react'
import {
  Form, Icon, Input, Button, Checkbox, message,
} from 'antd';
import axios from "axios";
import style from './index.css';


class LoginForm extends React.Component {

  handleRegister = (e) => {
    e.preventDefault()
    this.props.handleLoginOFF()
    this.props.handleRegisterOn()
   }

  handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
        axios.post('/api/v1/login', values)
        .then((value) => {
          console.log(value.data)
          message.success('登录成功')
          this.props.onSubmit(value.data)
          // window.location = '/'
        })
        .catch(err => {
          message.error(err)
          })
      }
    });
  }
  render() {
    const { getFieldDecorator } = this.props.form;
    return (
      <Form onSubmit={this.handleSubmit} className={style.login_form}>
        <Form.Item>
          {getFieldDecorator('username', {
            rules: [{ required: true, message: '请输入你的昵称!' }],
          })(
            <Input prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Username" />
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('password', {
            rules: [{ required: true, message: '请输入你的密码!' }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Password" />
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('remember', {
            valuePropName: 'checked',
            initialValue: true,
          })(
            <Checkbox>记住</Checkbox>
          )}
          <a className= {style.login_form_forgot} href="">忘记密码</a>
          <Button type="primary" htmlType="submit" className={style.login_form_button}>
            登录
          </Button>
          Or <a onClick={this.handleRegister}>注册!</a>
        </Form.Item>
      </Form>
    );
  }
}
export default Form.create()(LoginForm)


