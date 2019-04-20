'use strict'

import React from 'react'
import { Layout, Divider, Menu, Modal, Icon, Dropdown, message } from 'antd'
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
const SubMenu = Menu.SubMenu;


@withRouter
@inject('sysStore', 'userActions', 'userStore')
@observer
class Main extends React.Component {
  state = {version: undefined, user: undefined, role:0, visibleRegister:false, visibleLogin:false}

  async componentWillMount() {
    console.log(this.state.user)
    setTimeout(1000)
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

  handleLogin = (e) => {
    console.log(e)
    this.setState({ user: e ,  role:e.role, visibleLogin:false})
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
  GetHeadder = (e) => {
     let headers = null
     if (this.state.user === undefined){
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
            <a className="ant-dropdown-link" href="javascript:void(0)">{this.state.user.username}<Icon type="down" /></a>
          </Dropdown>
    }
    return headers
  }
  GetMenu = (item) => {
    let menu = null
    let sub = item.subMenu
    if(sub){
      menu = <SubMenu key="sub1" title={<span><Icon type="mail" /><span>管理模块</span></span>}>
            {
              sub
                .filter(item => item.inMenu && item.role<=this.state.role)
                .map(item => (
                  <Menu.Item key={item.url}>
                    <Link to={item.url}>
                      <span className='nav-text'>{item.name}</span>
                    </Link>
                  </Menu.Item>
              ))
            }
          </SubMenu>
    }
    else {
      menu = <Menu.Item key={item.url}>
                <Link to={item.url}>
                  <Icon type={item.icon} />
                  <span className='nav-text'>{item.name}</span>
                </Link>
              </Menu.Item>
    }
    return menu
  }

  GetSider = (e) => {
    let menu = null
    Menus.filter(item => item.inMenu && item.role<=this.state.role)
      .map((item) =>  {
        let result = this.GetMenu(item)
        console.log(result)
        if(menu){
          menu += result
        }
        else{
          menu = result
        }
        })
    return menu
  }

  render() {

    let headers = this.GetHeadder()
    // let menu = this.GetSider()
    // console.log(menu)
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
                .filter(item => item.inMenu && item.role<=this.state.role)
                .map((item) => {
                    let menu = this.GetMenu(item)
                    return menu
                  })
            }
          </Menu>
        </Sider>
        <Layout className={styles.Container}>
          <Header className={styles.Header}>
            {headers}
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
