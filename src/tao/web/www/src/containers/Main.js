'use strict'

import React from 'react'
import { Layout, Divider, Menu, Modal, Icon, Dropdown, message, Form, Input, Button, Checkbox } from 'antd'
import { inject, observer } from 'mobx-react'
import { Switch, withRouter, Route, Link } from 'react-router-dom'
import axios from 'axios'

import logo from '../logo.svg'
import Menus from '../menu'
import { Externals } from '../externals'
import styles from './Main.css'
import Overview from './overview'
import { LoginForm, RegistrationForm } from './user'


const { Header, Content, Footer, Sider } = Layout


@withRouter
@inject('sysStore', 'userActions', 'userStore')
@observer
class Main extends React.Component {
  state = {version: undefined, user: {}, visibleRegister:false, visibleLogin:false}

  async componentWillMount() {
    
    // await axios.all([
    //   axios.get('/api/v1/version'),
    //   axios.get('/api/v1/user'),
    // ])
    // .then(axios.spread((versionResp, userResp) => {
    //   this.setState({
    //     version: versionResp.data.version,
    //     user: {name: userResp.data.name, username: userResp.data.username}
    //   })
    // }))
    // .catch(err => {
    //   message.error('读取用户信息失败')
    // })
  }
  handleLoginOn = (e) => {
    this.setState({ visibleLogin:true})
  }
  handleRegisterOn = (e) => {
    this.setState({ visibleRegister:true})
  }
  handleLoginOFF= (e) => {
    this.setState({ visibleLogin:false})
  }
   handleRegisterOut = (e) => {
    this.setState({ visibleRegister:false})
  }

  handleRegisterSuccess = (e) => {
    this.setState({ visibleRegister:false, visibleLogin:true})
  }
  handleSubmitLogin = (e) => {
    axios.get('/api/v1/login')
      .then(() => {
        message.success('登录成功')
        window.location = '/'
        this.handleLoginOFF()
      })
      .catch(err => {
        message.error('logout失败')
      })
  }

  handleLogin = (e, value) => {
    this.setState({ user: value})
  }
  handleLogout = (e) => {
    axios.get('/api/v1/logout')
      .then(() => {
        message.success('已注销')
        window.location = '/'
      })
      .catch(err => {
        message.error('logout失败')
      })
  }

  render() {

    let headers = null
    if (this.state.user){
      headers = <span>
                  <span className='nav-text'><a onClick={this.handleRegisterOn}>注册</a></span>
                  <Divider  type='vertical'/>
        <span className='nav-text'><a onClick={this.handleLoginOn}>登录</a></span>
                </span>
    }
    else{
      headers =
          <Dropdown overlay={
            <Menu>
              <Menu.Item key='logout'>
                <a href='javascript:void(0)' onClick={this.handleLogout}>
                  Logout
                </a>
              </Menu.Item>
            </Menu>
          }>
            <a className="ant-dropdown-link" href="javascript:void(0)">{this.state.user.user_name}<Icon type="down" /></a>
          </Dropdown>
    }

    return (
      <Layout>
        <Sider className={styles.Sider}>
          <div><img src={logo} className={styles.Logo} alt='TAF online' /></div>
          <Menu
            theme='dark'
            mode='inline'
            defaultSelectedKeys={[Menus[0].url]}
            selectedKeys={[this.props.location.pathname]}
          >
            {
              Menus
                .filter(item => item.inMenu)
                .map(item => (
                  <Menu.Item key={item.url}>
                    <Link to={item.url}>
                      <Icon type={item.icon} />
                      <span className='nav-text'>{item.name}</span>
                    </Link>
                  </Menu.Item>
              ))
            }
          </Menu>
        </Sider>
        <Layout className={styles.Container}>
          <Header className={styles.Header}>
            {headers
            // Externals.map((e, idx) => (
            //     <span key={e.name} >
            //     {
            //       e.children === undefined ?
            //       <a href={e.url} target='_blank' rel='noopener noreferrer'>
            //         {e.name}
            //       </a> :
            //       <Dropdown overlay={
            //         <Menu>
            //           {
            //             e.children.map(e =>(
            //               <Menu.Item key={e.name}>
            //                 <a href={e.url} target='_blank' rel='noopener noreferrer'>
            //                   {e.name}
            //                 </a>
            //               </Menu.Item>
            //             ))
            //           }
            //         </Menu>
            //       }>
            //         <a className="ant-dropdown-link" href="javascript:void(0)">{e.name}<Icon type="down" /></a>
            //       </Dropdown>
            //     }
            //     {
            //       idx+1 !== Externals.length && <Divider type='vertical'/>
            //     }
            //   </span>
            // ))
          }
          </Header>
          <Modal
          title="注册"
          width={340}
          visible={this.state.visibleRegister}
          onOk={this.handleOk}
          onCancel={this.handleRegisterOut}
          footer={null}
          >
          <RegistrationForm onSubmit={this.handleRegisterSuccess}/>
          </Modal>
          <Modal
          title="登录"
          width={360}
          visible={this.state.visibleLogin}
          onCancel={this.handleLoginOFF}
          footer={null}
          >
          <LoginForm onSubmit={this.handleLogin}/>
          </Modal>
          <Content className={styles.Content}>
            <Switch>
              <Route key={'/'} path='/' exact component={Overview}/>
              {
                Menus.map(item => (
                  <Route key={item.url} path={item.url} exact component={item.component}/>
                ))
              }
            </Switch>
          </Content>
          <Footer className={styles.Footer}>
            fun<sup>{this.state.version || ''}</sup> ©2019 Created by QiuYing Xu.
          </Footer>
        </Layout>
      </Layout>
    )
  }
}

export default Main
