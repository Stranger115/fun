import React from 'react'
import Tasks from './containers/tasks'
import TaskDetail from './containers/tasks/detail'
import Deploy from './containers/deploy'
import Feature from './containers/feature'
import FeatureDetail from './containers/feature/detail'
import Release from './containers/release'
import ReleaseDetail from './containers/release/detail'
import ProductsManager from './containers/products'
import ModulesManager from './containers/modules'
import EnvsManager from './containers/environments'
import DNSManager from './containers/dns'
import Store from './containers/store'
import Admin from './containers/admin'


export default [
  {
    name: '商品列表',
    url: '/store:id',
    icon: 'shopping-cart',
    component: Store,
    inMenu: true,
    role:0x00,
    subMenu:null,
  },
  {
    name: '管理模块',
    url: '/admin',
    icon: 'schedule',
    component: Admin,
    inMenu: true,
    role: 0,//0xff,
    subMenu:[
      {
        name: '会员管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      },
      {
        name: '商品管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      },
      {
        name: '账单管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      }
    ],
  }
]
