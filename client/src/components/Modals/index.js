import React from 'react'
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles'

import LoginModal from './LoginModal'
import SignupModal from './SignupModal'

export default function Modals() {

  const theme = createMuiTheme({
    shape: {
      borderRadius: "20px"
    }
  })

  return (
    <MuiThemeProvider theme={theme}>
      <LoginModal />
      <SignupModal />
    </MuiThemeProvider>
  )
}
