'use strict'

import React from 'react'
import {Form, Select, Modal, Input, Row, Col, Icon, Button, message} from 'antd'
import axios from "axios";
import { FormItemLayout, FormItemLayoutWithOutLabel } from "../../constants"

const FormItem = Form.Item
const Option = Select.Option
export const EditableContext = React.createContext()

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
)


export const EditableFormRow = Form.create()(EditableRow)

export class EditableCell extends React.Component {
  constructor(props) {
    super(props)
    this.role = null
    }
  getInput = () => {
    if (this.props.dataIndex === 'role'){
      axios.get('/api/v1/get_role')
      .then(resp => {
         this.roles = resp.data.roles
         this.role = this.role.filter(item => item.level === 0)
      })
      return <Select initialValue="1">
              {
                <Option value="1">女</Option>
              }
             </Select>

    }
    else if (this.props.dataIndex === 'sex'){
      return <Select initialValue="1">
               <Option value="1">女</Option>
               <Option value="2">男</Option>
             </Select>
    }

    return <Input style={{ width: '70%' }} />
  }
  render() {
    const {
      editing,
      dataIndex,
      title,
      inputType,
      record,
      index,
      ...restProps
    } = this.props
    return (
      <EditableContext.Consumer>
        {(form) => {
          const { getFieldDecorator } = form
          return (
            <td {...restProps}>
              {editing ? (
                <FormItem style={{ margin: 0 }}>
                  {getFieldDecorator(dataIndex, {
                    rules: [{
                      required: true,
                      message: `请输入 ${title}!`,
                    }],
                    initialValue: record[dataIndex],
                  })(this.getInput())}
                </FormItem>
              ) : restProps.children}
            </td>
          )
        }}
      </EditableContext.Consumer>
    )
  }
}


function hasErrors(fieldsError) {
  return Object.keys(fieldsError).some(field => fieldsError[field])
}


export class UserForm extends React.Component {
  componentDidMount() {
    // To disabled submit button at the beginning.
    this.props.form.validateFields()
  }

  handleSubmit = (e) => {
    e.preventDefault()
    this.props.form.validateFields((err, values) => {
      if (!err) {
        this.props.onSubmit(values)
      }
    })
  }
  render() {
    const {
      getFieldDecorator, getFieldsError, getFieldError, isFieldTouched,
    } = this.props.form

    const prefixSelector = getFieldDecorator('prefix', {
      initialValue: '86',
    })(
      <Select style={{ width: 70 }}>
        <Option value="86">+86</Option>
        <Option value="87">+87</Option>
      </Select>
    );

    // Only show error after a field is touched.
    const usernameError = isFieldTouched('username') && getFieldError('username')
    const sexError = isFieldTouched('sex') && getFieldError('sex')
    const phoneError = isFieldTouched('phone') && getFieldError('phone')
    const roleError = isFieldTouched('role') && getFieldError('role')
    return (
      <Form onSubmit={this.handleSubmit}>
        <Form.Item
          {...FormItemLayout}
          validateStatus={usernameError ? 'error' : ''}
          help={usernameError || ''}
          label='用户名'
        >
            {getFieldDecorator('username', {
            rules: [{ required: true, message: '请输入用户名!' }],
          })(
              <Input placeholder="请输入用户名" />
          )}
        </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={sexError ? 'error' : ''}
          help={sexError || ''}
          label='sex'
        >
          {getFieldDecorator('sex', {
           rules: [{ required: true, message: '请选择性别!' }],
          })(
            <Select placeholder="请选择性别">
              <Option value="1">女</Option>
              <Option value="2">男</Option>
            </Select>
         )}
         </Form.Item>
        <Form.Item
          {...FormItemLayout}
          validateStatus={phoneError ? 'error' : ''}
          help={phoneError || ''}
          label='电话'
        >
          {getFieldDecorator('phone', {
            initialValue:'intranet',
            rules: [{ required: true,  message: '请输入电话!' }],
          })(
            <Input addonBefore={prefixSelector} style={{ width: '100%' }} />
          )}
        </Form.Item>
        <Form.Item {...FormItemLayoutWithOutLabel}>
          <Button
            type="primary"
            htmlType="submit"
            disabled={hasErrors(getFieldsError())}
          >
            提交
          </Button>
        </Form.Item>
      </Form>
    )
  }
}

export default Form.create()(UserForm)


